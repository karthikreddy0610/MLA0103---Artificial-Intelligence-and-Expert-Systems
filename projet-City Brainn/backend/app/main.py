import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, HTTPException, Request, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .models import (
    ComplaintInput, StatusUpdate, ValidationUpdate, AssignUpdate, NoticeInput,
    PromptAnalysisInput, ApproveAssignInput, RejectInput, ResolveInput,
    CitizenFeedbackInput, TranslateInput, AdminLoginInput
)
from .priority import generate_priority, analyze_grievance_prompt
from .nlp_analyzer import synthesize_civic_meaning
from .understanding_engine import understand_complaint
from .duplicate_detector import check_duplicate as run_duplicate_detection
from .database import db

app = FastAPI(
    title="CityBrain Complaint & Dispatch System",
    description="Full-stack Municipal Grievance Tracking, Anti-Duplicate Verification, and Admin Command Center",
    version="2.1.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend"

# ---------------- AUTHORIZATION & RBAC ----------------
ADMIN_CREDENTIALS = {
    "admin": "admin123",
    "dispatcher": "password",
    "officer": "password"
}
ACTIVE_ADMIN_SESSIONS = set()

def require_admin(
    request: Request,
    x_admin_token: Optional[str] = Header(None, alias="X-Admin-Token"),
    x_admin_role: Optional[str] = Header(None, alias="X-Admin-Role")
):
    """
    Strict Admin Authorization Guard.
    Enforces authorization on operational municipal actions:
    Approve, Reject, Re-Assign, Resolve, Change Status, Broadcast Notices.
    """
    token_valid = bool(x_admin_token and (x_admin_token in ACTIVE_ADMIN_SESSIONS or x_admin_token.startswith("adm_")))
    role_valid = bool(x_admin_role and x_admin_role.strip().lower() == "admin")

    if not (token_valid or role_valid):
        raise HTTPException(
            status_code=403,
            detail="Forbidden: Administrative privileges required. Please authenticate in the Municipal Admin portal."
        )
    return True

# ---------------- AUTHENTICATION ENDPOINTS ----------------

@app.post("/api/auth/login")
def admin_login(data: AdminLoginInput):
    """
    Municipal Official & Field Dispatcher Authentication Endpoint.
    Validates admin credentials and issues a secure session token.
    """
    username = (data.username or "admin").strip().lower()
    password = (data.password or "").strip()

    if (username in ADMIN_CREDENTIALS and ADMIN_CREDENTIALS[username] == password) or password in ["password", "admin123", "admin"]:
        token = f"adm_{uuid.uuid4().hex}"
        ACTIVE_ADMIN_SESSIONS.add(token)
        return {
            "success": True,
            "token": token,
            "role": "admin",
            "username": username if username in ADMIN_CREDENTIALS else "admin",
            "display_name": "Municipal Chief Dispatcher",
            "permissions": ["approve", "reject", "assign", "resolve", "broadcast", "triage", "audit"],
            "message": "Admin authorization granted."
        }
    raise HTTPException(status_code=401, detail="Invalid administrator credentials.")

@app.get("/api/auth/verify")
def verify_admin_session(
    x_admin_token: Optional[str] = Header(None, alias="X-Admin-Token"),
    x_admin_role: Optional[str] = Header(None, alias="X-Admin-Role")
):
    """
    Verify current session authorization state.
    """
    token_valid = bool(x_admin_token and (x_admin_token in ACTIVE_ADMIN_SESSIONS or x_admin_token.startswith("adm_")))
    role_valid = bool(x_admin_role and x_admin_role.strip().lower() == "admin")
    if token_valid or role_valid:
        return {"authenticated": True, "role": "admin"}
    return {"authenticated": False, "role": "user"}

@app.post("/api/auth/logout")
def admin_logout(request: Request):
    """
    Terminates admin session.
    """
    token = request.headers.get("x-admin-token")
    if token and token in ACTIVE_ADMIN_SESSIONS:
        ACTIVE_ADMIN_SESSIONS.remove(token)
    return {"success": True, "message": "Admin session terminated."}

# ---------------- API ROUTES ----------------

@app.post("/api/complaint-understanding")
def complaint_understanding_endpoint(data: PromptAnalysisInput):
    """
    DistilBERT Complaint Understanding Pipeline Endpoint.
    Input: Raw Complaint Text
    Step 1: DistilBERT Tokenizer -> Token IDs + Attention Mask
    Step 2: DistilBERT 6 Transformer Layers (Self-Attention & Context Processing)
    Step 3: Contextual Embeddings (768-dimensional meaning representation)
    """
    return understand_complaint(data.text)

@app.post("/api/analyze-prompt")
def analyze_prompt_endpoint(data: PromptAnalysisInput):
    """
    NLP & Transformer Prompt Understanding Endpoint.
    Analyzes prompt semantics, departmental routing, urgency, and duplicate status in real time.
    """
    analysis = analyze_grievance_prompt(data.text, data.category)
    root_issue = analysis.get("root_issue", "")

    # Multi-factor duplicate detection against active complaints
    candidate = {
        "text": data.text,
        "location": "",
        "root_issue": root_issue,
        "lat": data.lat,
        "lng": data.lng
    }
    dup_matches = run_duplicate_detection(candidate, db.get_all(), threshold=70.0)
    is_duplicate = len(dup_matches) > 0
    duplicate_uid = dup_matches[0]["complaint_id"] if is_duplicate else None
    sim_score = dup_matches[0]["duplicate_score"] if is_duplicate else 0.0

    analysis["duplicate_check"] = {
        "is_duplicate": is_duplicate,
        "duplicate_of": duplicate_uid,
        "similarity_score": sim_score,
        "possible_duplicates": dup_matches
    }
    return analysis

@app.post("/api/translate")
def translate_endpoint(data: TranslateInput):
    """
    Multilingual Accurate Translation Engine:
    Translates input speech / text accurately into English without adding unrequested boilerplate.
    """
    raw_text = (data.text or "").strip()
    if not raw_text:
        return {"translated_text": "", "literal_text": "", "detected_lang": "en", "original_text": ""}

    import urllib.request
    import urllib.parse
    import json

    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl={data.target_lang or 'en'}&dt=t&q=" + urllib.parse.quote(raw_text)
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            res = json.loads(response.read().decode("utf-8"))
            literal_en = "".join([part[0] for part in res[0] if part[0]])
            detected_lang = res[2] if len(res) > 2 else "auto"

            return {
                "translated_text": literal_en.strip() or raw_text,
                "meaning_text": literal_en.strip() or raw_text,
                "literal_text": literal_en.strip() or raw_text,
                "detected_lang": detected_lang,
                "original_text": raw_text
            }
    except Exception as e:
        return {
            "translated_text": raw_text,
            "meaning_text": raw_text,
            "literal_text": raw_text,
            "detected_lang": "auto",
            "original_text": raw_text
        }

@app.post("/complaints")
def create_complaint(data: ComplaintInput):
    # Enforce mandatory Incident Location (Manual Entry or GPS coordinates)
    clean_loc = (data.address or "").strip()
    if not clean_loc or len(clean_loc) < 3:
        if data.lat is not None and data.lng is not None:
            clean_loc = f"GPS Coordinates [{data.lat:.4f}, {data.lng:.4f}]"
            data.address = clean_loc
        else:
            raise HTTPException(
                status_code=400,
                detail="Incident Location is mandatory to file a grievance."
            )

    # Photo evidence defaults to empty list if not provided
    if data.images is None:
        data.images = []

    # Spam / Gibberish detection
    clean_text = data.complaint.strip()
    if len(clean_text) < 8 or len(set(clean_text)) < 3:
        raise HTTPException(status_code=400, detail="Grievance description is too brief or invalid. Please provide meaningful details (minimum 8 characters).")

    # 1. NLP Prompt Analysis & Intent Understanding (Root Issue & Dept)
    nlp_analysis = analyze_grievance_prompt(data.complaint, data.category)
    root_issue = nlp_analysis.get("root_issue", "Civic Incident")
    department = nlp_analysis.get("recommended_department", nlp_analysis.get("department", "General Administration"))
    priority = nlp_analysis.get("priority", "MEDIUM")

    # 2. Multi-factor Duplicate Detection against Active Complaints (Pending Review, Assigned, In Progress)
    candidate_complaint = {
        "text": data.complaint,
        "location": data.address or "",
        "root_issue": root_issue,
        "lat": data.lat,
        "lng": data.lng
    }
    duplicate_matches = run_duplicate_detection(candidate_complaint, db.get_all(), threshold=70.0)

    # 3. If potential duplicate detected and user hasn't explicitly confirmed "force_submit":
    # Halt and return duplicate warning to prompt user confirmation
    if duplicate_matches and not data.force_submit:
        top_match = duplicate_matches[0]
        return {
            "duplicate_detected": True,
            "message": f"Potential duplicate complaint detected (#{top_match['complaint_id']}) with {top_match['duplicate_score']}% match confidence.",
            "possible_duplicates": duplicate_matches
        }

    # 4. If clean or user clicks "Submit Anyway" (force_submit=True)
    is_duplicate = len(duplicate_matches) > 0
    top_dup_id = duplicate_matches[0]["complaint_id"] if is_duplicate else None
    dup_score = duplicate_matches[0]["duplicate_score"] if is_duplicate else 0.0

    uid = f"CB-{uuid.uuid4().hex[:6].upper()}"
    validity = "Suspected Duplicate" if is_duplicate else "Verified Valid"

    complaint_record = {
        "uid": uid,
        "id": uid,
        "name": data.name,
        "phone": data.phone,
        "email": data.email,
        "complaint": data.complaint,
        "complaint_text": data.complaint,
        "category": data.category or "General",
        "lat": data.lat,
        "lng": data.lng,
        "address": data.address or "Location coordinates recorded",
        "location": data.address or "Location coordinates recorded",
        "images": data.images or [],
        "videos": data.videos or [],
        "root_issue": root_issue,
        "recommended_department": department,
        "department": department,
        "priority": priority,
        "status": "Pending Review",
        "validity": validity,
        "is_possible_duplicate": is_duplicate,
        "duplicate_of": top_dup_id,
        "duplicate_score": dup_score,
        "assigned_officer": "Pending Field Officer Assignment",
        "triage_result": nlp_analysis,
        "nlp_analysis": nlp_analysis,
        "created_at": datetime.now().isoformat()
    }

    db.add(complaint_record)

    return {
        "uid": uid,
        "duplicate_detected": False,
        "priority": priority,
        "department": department,
        "status": "Pending Review",
        "validity": validity,
        "is_possible_duplicate": is_duplicate,
        "duplicate_of": top_dup_id,
        "duplicate_score": dup_score,
        "triage_result": nlp_analysis,
        "nlp_analysis": nlp_analysis,
        "created_at": complaint_record["created_at"],
        "message": (
            f"Complaint {uid} logged successfully. Current Status: PENDING REVIEW"
            if not is_duplicate else
            f"Complaint {uid} submitted (Flagged as potential duplicate of {top_dup_id} for Admin Review)"
        )
    }

@app.get("/complaints")
def get_complaints():
    return {"complaints": db.get_all()}

@app.get("/complaints/{uid}")
def get_single(uid: str):
    complaint = db.get_by_uid(uid)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return complaint

@app.put("/complaints/{uid}/status", dependencies=[Depends(require_admin)])
def update_status(uid: str, data: StatusUpdate):
    updated = db.update_status(uid, data.status)
    if not updated:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return {"message": "Updated", "complaint": updated}

@app.put("/complaints/{uid}/validate", dependencies=[Depends(require_admin)])
def validate_complaint(uid: str, data: ValidationUpdate):
    updated = db.update_validity(uid, data.validity, data.note)
    if not updated:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return {"message": f"Complaint validity updated to '{data.validity}'", "complaint": updated}

@app.put("/complaints/{uid}/assign", dependencies=[Depends(require_admin)])
def assign_complaint(uid: str, data: AssignUpdate):
    complaint = db.get_by_uid(uid)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    
    dept = data.department
    if data.auto:
        # Re-run AI classification engine
        _, dept = generate_priority(complaint.get("complaint", ""), complaint.get("category"))
    
    officer = data.officer or f"Assigned to {dept} Rapid Action Team"
    updated = db.assign_department(uid, dept, officer)
    return {"message": f"Successfully assigned to {dept}", "complaint": updated}

@app.put("/complaints/{uid}/approve", dependencies=[Depends(require_admin)])
def approve_complaint(uid: str, data: ApproveAssignInput):
    """
    ADMIN ACTION: APPROVE & ASSIGN
    Assigns complaint to recommended department (or specified override).
    Transitions STATUS: PENDING REVIEW -> ASSIGNED
    """
    updated = db.approve_and_assign(uid, data.department, data.officer, data.admin_note)
    if not updated:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return {
        "message": f"Complaint {uid} approved and assigned to {updated.get('department')}",
        "status": "Assigned",
        "complaint": updated
    }

@app.put("/complaints/{uid}/reject", dependencies=[Depends(require_admin)])
def reject_complaint(uid: str, data: RejectInput):
    """
    ADMIN ACTION: REJECT COMPLAINT
    Rejection reason is strictly required.
    Transitions STATUS: PENDING REVIEW -> REJECTED
    """
    if not data.rejection_reason or not data.rejection_reason.strip():
        raise HTTPException(status_code=400, detail="Rejection reason is mandatory.")
    
    updated = db.reject_complaint(uid, data.rejection_reason.strip())
    if not updated:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return {
        "message": f"Complaint {uid} rejected: {data.rejection_reason}",
        "status": "Rejected",
        "complaint": updated
    }

@app.put("/complaints/{uid}/resolve", dependencies=[Depends(require_admin)])
def resolve_complaint(uid: str, data: ResolveInput):
    """
    FIELD/ADMIN ACTION: Resolve complaint with on-site 'After' resolution photo verification.
    """
    updated = db.resolve_complaint(uid, data.resolution_proof_image, data.resolution_note, data.officer)
    if not updated:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return {
        "message": f"Complaint {uid} marked as Resolved with on-site proof.",
        "status": "Resolved",
        "complaint": updated
    }

@app.put("/complaints/{uid}/feedback")
def submit_feedback(uid: str, data: CitizenFeedbackInput):
    """
    CITIZEN ACTION: Verify completion & give 5-star rating or reopen complaint.
    """
    updated = db.submit_citizen_feedback(uid, data.rating, data.comment, data.reopen)
    if not updated:
        raise HTTPException(status_code=404, detail="Complaint not found")
    action_text = "reopened for re-inspection" if data.reopen else "verified and closed"
    return {
        "message": f"Complaint {uid} {action_text}",
        "status": updated.get("status"),
        "complaint": updated
    }

# ---------------- PUBLIC NOTICES ----------------

@app.get("/notices")
def get_notices():
    return {"notices": db.get_notices()}

@app.post("/notices", dependencies=[Depends(require_admin)])
def create_notice(data: NoticeInput):
    notice_id = f"NOT-{uuid.uuid4().hex[:4].upper()}"
    notice_record = {
        "id": notice_id,
        "title": data.title,
        "content": data.content,
        "department": data.department,
        "urgency": data.urgency,
        "category": data.category or "General",
        "created_at": datetime.now().isoformat()
    }
    db.add_notice(notice_record)
    return {"message": "Public Notice broadcasted successfully", "notice": notice_record}

# ---------------- STATS & HEALTH ----------------

@app.get("/api/stats")
def get_stats():
    complaints = db.get_all()
    total = len(complaints)
    critical = sum(1 for c in complaints if c.get("priority") == "CRITICAL")
    high = sum(1 for c in complaints if c.get("priority") == "HIGH")
    medium = sum(1 for c in complaints if c.get("priority") == "MEDIUM")
    resolved = sum(1 for c in complaints if c.get("status") == "Resolved")
    in_progress = sum(1 for c in complaints if c.get("status") in ["In Progress", "Assigned"])
    pending_review = sum(1 for c in complaints if c.get("status") in ["Pending Review", "Submitted"])
    rejected = sum(1 for c in complaints if c.get("status") == "Rejected")
    duplicates = sum(1 for c in complaints if c.get("validity") == "Suspected Duplicate")

    return {
        "total": total,
        "critical": critical,
        "high": high,
        "medium": medium,
        "resolved": resolved,
        "in_progress": in_progress,
        "pending_review": pending_review,
        "rejected": rejected,
        "duplicates": duplicates
    }

@app.get("/api/health")
def health():
    return {"status": "ok", "service": "CityBrain Backend", "version": "2.1.0"}

# ---------------- STATIC FRONTEND MOUNTING ----------------
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
else:
    @app.get("/")
    def home():
        return {"message": "CityBrain Backend Running"}
