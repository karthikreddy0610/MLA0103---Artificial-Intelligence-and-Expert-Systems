import json
import re
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Tuple

DB_DIR = Path(__file__).resolve().parent.parent / "data"
COMPLAINTS_FILE = DB_DIR / "complaints.json"
NOTICES_FILE = DB_DIR / "notices.json"

class Database:
    def __init__(self):
        self.complaints = []
        self.notices = []
        self._load()

    def _load(self):
        try:
            if COMPLAINTS_FILE.exists():
                with open(COMPLAINTS_FILE, "r", encoding="utf-8") as f:
                    self.complaints = json.load(f)
            else:
                self._seed_initial_complaints()
        except Exception:
            self._seed_initial_complaints()

        try:
            if NOTICES_FILE.exists():
                with open(NOTICES_FILE, "r", encoding="utf-8") as f:
                    self.notices = json.load(f)
            else:
                self._seed_initial_notices()
        except Exception:
            self._seed_initial_notices()

    def _seed_initial_complaints(self):
        self.complaints = [
            {
                "uid": "CB-1092F1",
                "name": "Sarah Jenkins",
                "phone": "+1 555-019-2834",
                "email": "sarah.j@example.com",
                "complaint": "Major water pipe burst near central market intersection flooding pedestrian walkway.",
                "category": "Water",
                "lat": 37.7749,
                "lng": -122.4194,
                "address": "Market St & 5th Ave, Central District",
                "images": ["https://images.unsplash.com/photo-1544717305-2782549b5136?auto=format&fit=crop&w=400&q=80"],
                "videos": [],
                "priority": "HIGH",
                "department": "Water Supply & Sewerage Board",
                "status": "In Progress",
                "validity": "Verified Valid",
                "assigned_officer": "Eng. Robert Thorne",
                "created_at": "2026-11-01T08:15:00"
            },
            {
                "uid": "CB-8491C2",
                "name": "Marcus Vance",
                "phone": "+1 555-014-8821",
                "email": "m.vance@example.com",
                "complaint": "Severe sparking and smoke coming from residential electric transformer pole.",
                "category": "Electricity",
                "lat": 37.7833,
                "lng": -122.4167,
                "address": "42 Pine Street, Downtown",
                "images": [],
                "videos": [],
                "priority": "CRITICAL",
                "department": "Electricity & Power Board",
                "status": "Pending Review",
                "validity": "Verified Valid",
                "assigned_officer": "Pending Field Officer Assignment",
                "triage_result": {
                    "root_issue": "High-Voltage Transformer / Live Spark Hazard",
                    "recommended_department": "Electricity & Power Board",
                    "priority": "CRITICAL",
                    "explanation": "Active electrical arcing on residential pole with electrocution & fire hazard."
                },
                "created_at": "2026-11-02T03:40:00"
            },
            {
                "uid": "CB-3718A9",
                "name": "Priya Sharma",
                "phone": "+1 555-018-9943",
                "email": "priya.s@example.com",
                "complaint": "Deep dangerous pothole damaging vehicles on eastbound lane of Park Avenue.",
                "category": "Roads",
                "lat": 37.7690,
                "lng": -122.4467,
                "address": "Park Ave near Elm St",
                "images": [],
                "videos": [],
                "priority": "HIGH",
                "department": "Public Works Department (PWD)",
                "status": "Resolved",
                "validity": "Verified Valid",
                "assigned_officer": "Officer David Cole",
                "created_at": "2026-10-30T14:22:00"
            }
        ]
        self._save_complaints()

    def _seed_initial_notices(self):
        self.notices = [
            {
                "id": "NOT-881",
                "title": "Scheduled Water Pipeline Maintenance in Central Ward",
                "content": "Water Supply Board will execute scheduled infrastructure maintenance on 5th Ave from 10:00 PM to 4:00 AM. Low pressure expected.",
                "department": "Water Supply & Sewerage Board",
                "urgency": "Alert",
                "category": "Water",
                "created_at": "2026-11-02T06:00:00"
            },
            {
                "id": "NOT-742",
                "title": "24/7 Mobile Emergency Ambulance Fleet Deployed",
                "content": "Four new rapid-response paramedic mobile units have been stationed near Civic Center to cut emergency transit times by 40%.",
                "department": "Emergency Healthcare & Ambulance Services",
                "urgency": "Info",
                "category": "Healthcare",
                "created_at": "2026-11-01T12:00:00"
            },
            {
                "id": "NOT-509",
                "title": "Monsoon Road Safety & Pothole Repair Blitz",
                "content": "PWD rapid action teams are resurfacing high-traffic corridors this weekend. Citizens can report road craters directly with GPS coordinates.",
                "department": "Public Works Department (PWD)",
                "urgency": "Info",
                "category": "Roads",
                "created_at": "2026-10-31T09:30:00"
            }
        ]
        self._save_notices()

    def _save_complaints(self):
        try:
            DB_DIR.mkdir(parents=True, exist_ok=True)
            with open(COMPLAINTS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.complaints, f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save complaints: {e}")

    def _save_notices(self):
        try:
            DB_DIR.mkdir(parents=True, exist_ok=True)
            with open(NOTICES_FILE, "w", encoding="utf-8") as f:
                json.dump(self.notices, f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save notices: {e}")

    # Anti-Duplicate / Anti-Fake NLP Engine
    def check_duplicate(self, text: str, lat: Optional[float] = None, lng: Optional[float] = None) -> Tuple[bool, Optional[str]]:
        is_dup, dup_uid, _ = self.check_duplicate_detailed(text, lat, lng)
        return is_dup, dup_uid

    def check_duplicate_detailed(self, text: str, lat: Optional[float] = None, lng: Optional[float] = None) -> Tuple[bool, Optional[str], float]:
        """
        NLP Semantic Cosine Similarity & Proximity Anti-Duplicate Verification Engine.
        Compares input prompt against existing municipal records using token overlap & GPS distance.
        """
        clean_text = (text or "").lower()
        words = set(re.findall(r"\w{3,}", clean_text))
        if not words or len(words) < 2:
            return False, None, 0.0

        best_score = 0.0
        best_match_uid = None

        for c in self.complaints[:30]:  # check recent 30 complaints
            existing_text = c.get("complaint", "").lower()
            existing_words = set(re.findall(r"\w{3,}", existing_text))
            if not existing_words:
                continue

            overlap = words.intersection(existing_words)
            # Jaccard / Cosine approximation
            similarity = len(overlap) / (len(words) + len(existing_words) - len(overlap))
            if similarity > best_score:
                best_score = similarity
                best_match_uid = c.get("uid")

            # High semantic text similarity threshold (> 60%)
            if len(words) >= 3 and similarity >= 0.60:
                return True, c.get("uid"), round(similarity, 3)

            # Geographic proximity: if within ~250m and overlapping keywords >= 2
            if lat is not None and lng is not None and c.get("lat") and c.get("lng"):
                dist = abs(lat - c["lat"]) + abs(lng - c["lng"])
                if dist < 0.0025 and len(overlap) >= 2:
                    return True, c.get("uid"), round(max(similarity, 0.75), 3)

        return False, None, round(best_score, 3)

    def get_all(self) -> List[dict]:
        return self.complaints

    def get_by_uid(self, uid: str) -> Optional[dict]:
        for c in self.complaints:
            if c.get("uid", "").upper() == uid.upper():
                return c
        return None

    def add(self, record: dict) -> dict:
        self.complaints.insert(0, record)
        self._save_complaints()
        return record

    def update_status(self, uid: str, new_status: str) -> Optional[dict]:
        for c in self.complaints:
            if c.get("uid", "").upper() == uid.upper():
                c["status"] = new_status
                c["updated_at"] = datetime.now().isoformat()
                self._save_complaints()
                return c
        return None

    def update_validity(self, uid: str, validity: str, note: Optional[str] = None) -> Optional[dict]:
        for c in self.complaints:
            if c.get("uid", "").upper() == uid.upper():
                c["validity"] = validity
                if note:
                    c["admin_note"] = note
                c["updated_at"] = datetime.now().isoformat()
                self._save_complaints()
                return c
        return None

    def assign_department(self, uid: str, department: str, officer: Optional[str] = None) -> Optional[dict]:
        for c in self.complaints:
            if c.get("uid", "").upper() == uid.upper():
                c["department"] = department
                if officer:
                    c["assigned_officer"] = officer
                c["status"] = "Assigned"
                c["updated_at"] = datetime.now().isoformat()
                self._save_complaints()
                return c
        return None

    def approve_and_assign(self, uid: str, department: Optional[str] = None, officer: Optional[str] = None, note: Optional[str] = None) -> Optional[dict]:
        """
        ADMIN ACTION: Approve complaint and dispatch to recommended department.
        STATUS transitions: PENDING REVIEW -> ASSIGNED
        """
        for c in self.complaints:
            if c.get("uid", "").upper() == uid.upper():
                dept = department or c.get("department") or "General Administration"
                c["department"] = dept
                c["assigned_officer"] = officer or f"Assigned to {dept} Rapid Action Unit"
                c["status"] = "Assigned"
                c["admin_decision"] = "APPROVED"
                if note:
                    c["admin_note"] = note
                c["approved_at"] = datetime.now().isoformat()
                c["updated_at"] = c["approved_at"]
                self._save_complaints()
                return c
        return None

    def reject_complaint(self, uid: str, rejection_reason: str) -> Optional[dict]:
        """
        ADMIN ACTION: Reject complaint with required rejection reason.
        STATUS transitions: PENDING REVIEW -> REJECTED
        """
        for c in self.complaints:
            if c.get("uid", "").upper() == uid.upper():
                c["status"] = "Rejected"
                c["validity"] = "Rejected/Spam"
                c["admin_decision"] = "REJECTED"
                c["rejection_reason"] = rejection_reason
                c["rejected_at"] = datetime.now().isoformat()
                c["updated_at"] = c["rejected_at"]
                self._save_complaints()
                return c
        return None

    def resolve_complaint(self, uid: str, resolution_proof_image: Optional[str] = None, resolution_note: Optional[str] = None, officer: Optional[str] = None) -> Optional[dict]:
        """
        FIELD/ADMIN ACTION: Mark complaint resolved with on-site resolution evidence photo.
        STATUS transitions: IN PROGRESS / ASSIGNED -> RESOLVED
        """
        for c in self.complaints:
            if c.get("uid", "").upper() == uid.upper():
                c["status"] = "Resolved"
                if resolution_proof_image:
                    c["resolution_proof_image"] = resolution_proof_image
                    c["after_image"] = resolution_proof_image
                if resolution_note:
                    c["resolution_note"] = resolution_note
                    c["resolution_notes"] = resolution_note
                if officer:
                    c["assigned_officer"] = officer
                    c["resolved_by"] = officer
                c["resolved_at"] = datetime.now().isoformat()
                c["updated_at"] = c["resolved_at"]
                self._save_complaints()
                return c
        return None

    def submit_citizen_feedback(self, uid: str, rating: int, comment: Optional[str] = None, reopen: bool = False) -> Optional[dict]:
        """
        CITIZEN ACTION: Confirm resolution or dispute/reopen grievance.
        """
        for c in self.complaints:
            if c.get("uid", "").upper() == uid.upper():
                if reopen:
                    c["status"] = "In Progress"
                    c["disputed"] = True
                    c["dispute_note"] = comment or "Citizen reported resolution was incomplete."
                    c["reopened_at"] = datetime.now().isoformat()
                    # Reopen escalates priority by one notch to prevent chronic neglect
                    curr_p = (c.get("priority") or "MEDIUM").upper()
                    if curr_p == "LOW":
                        c["priority"] = "MEDIUM"
                    elif curr_p == "MEDIUM":
                        c["priority"] = "HIGH"
                    elif curr_p == "HIGH":
                        c["priority"] = "CRITICAL"
                    c["reopened_count"] = c.get("reopened_count", 0) + 1
                else:
                    c["status"] = "Verified Closed"
                    c["citizen_verified"] = True

                c["citizen_rating"] = rating
                c["citizen_feedback"] = comment or ""
                c["citizen_feedback_detail"] = {
                    "rating": rating,
                    "comment": comment or "",
                    "reopened": reopen,
                    "submitted_at": datetime.now().isoformat()
                }
                c["updated_at"] = datetime.now().isoformat()
                self._save_complaints()
                return c
        return None

    def get_notices(self) -> List[dict]:
        return self.notices

    def add_notice(self, notice: dict) -> dict:
        self.notices.insert(0, notice)
        self._save_notices()
        return notice

db = Database()
