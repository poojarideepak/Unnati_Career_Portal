from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import date, datetime


# ── AUTH ──────────────────────────────────────────────
class StudentLoginReq(BaseModel):
    roll_no: str
    dob: str   # DD-MM-YYYY

class AdminLoginReq(BaseModel):
    email: str
    password: str

class TokenRes(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user_id: Optional[int]
    name: str


# ── STUDENT ──────────────────────────────────────────
class StudentCreate(BaseModel):
    name: str
    roll_no: str
    dob: str
    email: EmailStr
    phone: Optional[str] = None
    course: str
    cgpa: float = Field(ge=0, le=10)
    skills: Optional[str] = None
    batch: int

class StudentUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    cgpa: Optional[float] = Field(None, ge=0, le=10)
    skills: Optional[str] = None
    profile_photo: Optional[str] = None

class StudentOut(BaseModel):
    id: int
    name: str
    roll_no: str
    email: str
    phone: Optional[str]
    course: str
    cgpa: float
    skills: Optional[str]
    resume: Optional[str]
    batch: int
    is_placed: bool
    profile_photo: Optional[str] = None
    created_at: Optional[datetime]
    class Config: from_attributes = True

class StudentPublic(BaseModel):
    id: int
    name: str
    course: str
    cgpa: float
    batch: int
    is_placed: bool
    class Config: from_attributes = True


# ── COMPANY ──────────────────────────────────────────
class CompanyCreate(BaseModel):
    name: str
    sector: str
    pkg_range: Optional[str] = None
    roles: Optional[str] = None
    website: Optional[str] = None
    icon: Optional[str] = "🏢"
    rating: Optional[float] = 4.0

class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    sector: Optional[str] = None
    pkg_range: Optional[str] = None
    roles: Optional[str] = None
    website: Optional[str] = None
    icon: Optional[str] = None
    rating: Optional[float] = None

class CompanyOut(BaseModel):
    id: int
    name: str
    sector: str
    pkg_range: Optional[str]
    roles: Optional[str]
    website: Optional[str]
    icon: Optional[str]
    rating: float
    class Config: from_attributes = True


# ── JOB ──────────────────────────────────────────────
class JobCreate(BaseModel):
    company_id: int
    title: str
    description: Optional[str] = None
    course: str = "Any"
    min_cgpa: float = 0.0
    skills: Optional[str] = None
    salary: Optional[str] = None
    drive_date: Optional[date] = None

class JobUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    course: Optional[str] = None
    min_cgpa: Optional[float] = None
    skills: Optional[str] = None
    salary: Optional[str] = None
    drive_date: Optional[date] = None
    is_active: Optional[bool] = None

class JobOut(BaseModel):
    id: int
    company_id: int
    title: str
    description: Optional[str]
    course: str
    min_cgpa: float
    skills: Optional[str]
    salary: Optional[str]
    drive_date: Optional[date]
    is_active: bool
    company: Optional[CompanyOut]
    class Config: from_attributes = True


# ── APPLICATION ──────────────────────────────────────
class ApplicationCreate(BaseModel):
    job_id: int

class ApplicationStatusUpdate(BaseModel):
    status: str  # Applied | Shortlisted | Selected | Rejected

class ApplicationOut(BaseModel):
    id: int
    student_id: int
    job_id: int
    applied_on: Optional[date]
    status: str
    student: Optional[StudentPublic]
    job: Optional[JobOut]
    class Config: from_attributes = True


# ── NOTIFICATION ─────────────────────────────────────
class NotifOut(BaseModel):
    id: int
    student_id: Optional[int]
    message: str
    is_read: bool
    target: str
    created_at: Optional[datetime]
    class Config: from_attributes = True


# ── ALUMNI ───────────────────────────────────────────
class AlumniCreate(BaseModel):
    name: str
    batch: int
    course: str
    company: Optional[str] = None
    role: Optional[str] = None
    package: Optional[float] = None
    email: Optional[str] = None
    achievement: Optional[str] = None

class AlumniOut(BaseModel):
    id: int
    name: str
    batch: int
    course: str
    company: Optional[str]
    role: Optional[str]
    package: Optional[float]
    email: Optional[str]
    achievement: Optional[str]
    class Config: from_attributes = True


# ── INTERVIEW FORMS ───────────────────────────────────
class IFormCreate(BaseModel):
    company_id: int
    job_id: int
    form_url: str
    note: Optional[str] = None

class IFormOut(BaseModel):
    id: int
    company_id: int
    job_id: int
    form_url: str
    note: Optional[str]
    is_active: bool
    class Config: from_attributes = True


# ── GENERIC ──────────────────────────────────────────
class MsgRes(BaseModel):
    message: str
    success: bool = True

class BroadcastReq(BaseModel):
    message: str
    course: Optional[str] = None # If set, send only to students in this course


# ── SCHOLARSHIP ──────────────────────────────────────
class ScholarshipCreate(BaseModel):
    title: str
    provider: str
    amount: Optional[str] = None
    deadline: Optional[date] = None
    description: Optional[str] = None
    eligibility: Optional[str] = None
    apply_url: Optional[str] = None

class ScholarshipOut(BaseModel):
    id: int
    title: str
    provider: str
    amount: Optional[str]
    deadline: Optional[date]
    description: Optional[str]
    eligibility: Optional[str]
    apply_url: Optional[str]
    is_active: bool
    class Config: from_attributes = True
