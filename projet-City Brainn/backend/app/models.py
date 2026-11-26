from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ComplaintInput(BaseModel):
    name: str
    phone: str
    email: str
    complaint: str
    category: Optional[str] = "General"
    lat: Optional[float] = None
    lng: Optional[float] = None
    address: Optional[str] = None
    images: List[str] = []
    videos: List[str] = []
    verification_code: Optional[str] = None
    force_submit: bool = False

class StatusUpdate(BaseModel):
    status: str
    note: Optional[str] = None

class ValidationUpdate(BaseModel):
    validity: str  # "Verified Valid", "Suspected Duplicate", "Rejected/Spam"
    note: Optional[str] = None

class AssignUpdate(BaseModel):
    department: str
    officer: Optional[str] = None
    auto: bool = False

class NoticeInput(BaseModel):
    title: str
    content: str
    department: str
    urgency: str = "Info"  # "Emergency", "Alert", "Info"
    category: Optional[str] = "General"

class PromptAnalysisInput(BaseModel):
    text: str
    category: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None

class ApproveAssignInput(BaseModel):
    department: Optional[str] = None
    officer: Optional[str] = None
    admin_note: Optional[str] = None

class RejectInput(BaseModel):
    rejection_reason: str

class ResolveInput(BaseModel):
    resolution_proof_image: Optional[str] = None
    resolution_note: Optional[str] = None
    officer: Optional[str] = None

class CitizenFeedbackInput(BaseModel):
    rating: int = 5
    comment: Optional[str] = None
    reopen: bool = False

class TranslateInput(BaseModel):
    text: str
    target_lang: Optional[str] = "en"

class AdminLoginInput(BaseModel):
    username: Optional[str] = "admin"
    password: str


