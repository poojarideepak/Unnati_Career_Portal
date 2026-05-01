from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from config import settings
import models, schemas
from auth_utils import create_token
from email_utils import trigger_email
from fastapi import BackgroundTasks

router = APIRouter()

@router.post("/student/login", response_model=schemas.TokenRes)
def student_login(payload: schemas.StudentLoginReq, db: Session = Depends(get_db)):
    student = db.query(models.Student).filter(models.Student.roll_no == payload.roll_no.strip()).first()
    if not student or student.dob != payload.dob.strip():
        raise HTTPException(status_code=401, detail="Invalid Roll Number or Date of Birth.")
    token = create_token({"sub": str(student.id), "role": "student"})
    return schemas.TokenRes(access_token=token, role="student", user_id=student.id, name=student.name)

@router.post("/admin/login", response_model=schemas.TokenRes)
def admin_login(payload: schemas.AdminLoginReq, db: Session = Depends(get_db)):
    if payload.email.strip() != settings.ADMIN_EMAIL or payload.password.strip() != settings.ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid admin credentials.")
    token = create_token({"sub": "0", "role": "admin"})
    return schemas.TokenRes(access_token=token, role="admin", user_id=0, name="Admin")

@router.post("/student/register", response_model=schemas.StudentOut, status_code=201)
def student_register(payload: schemas.StudentCreate, bg: BackgroundTasks, db: Session = Depends(get_db)):
    if db.query(models.Student).filter(models.Student.roll_no == payload.roll_no).first():
        raise HTTPException(status_code=400, detail="Roll number already registered.")
    if db.query(models.Student).filter(models.Student.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already registered.")
    student = models.Student(**payload.model_dump())
    db.add(student)
    db.commit()
    db.refresh(student)
    db.add(models.Notification(student_id=student.id, message="Welcome to Unnati Career Portal! 🎓 Browse jobs and apply.", target="student"))
    db.add(models.Notification(student_id=None, message=f"New student registered: {student.name} ({student.roll_no})", target="admin"))
    db.commit()
    
    # Welcome Email
    subject = "Welcome to Unnati Career Portal!"
    body = f"<h2>Hello {student.name},</h2><p>Welcome to Unnati Career Portal, your college placement portal!</p><p>You can now log in using your Roll Number ({student.roll_no}) and Date of Birth ({student.dob}) to browse job opportunities, view interview forms, and track your applications.</p><br><p>Best regards,<br>Placement Cell Team</p>"
    trigger_email(bg, subject, student.email, body)
    
    return student
