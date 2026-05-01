from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import date
from database import get_db
import models, schemas
from auth_utils import require_student, require_admin
from email_utils import trigger_email
from fastapi import BackgroundTasks

router = APIRouter()

def _app_q(db):
    return db.query(models.Application).options(
        joinedload(models.Application.student),
        joinedload(models.Application.job).joinedload(models.Job.company)
    )

@router.post("/", response_model=schemas.ApplicationOut, status_code=201)
def apply(payload: schemas.ApplicationCreate, bg: BackgroundTasks, current=Depends(require_student), db: Session = Depends(get_db)):
    s = current["user"]
    j = db.query(models.Job).options(joinedload(models.Job.company)).filter(models.Job.id == payload.job_id, models.Job.is_active == True).first()
    if not j: raise HTTPException(status_code=404, detail="Job not found or inactive.")
    if j.course != "Any" and j.course != s.course:
        raise HTTPException(status_code=403, detail="Not eligible — course mismatch.")
    if s.cgpa < j.min_cgpa:
        raise HTTPException(status_code=403, detail=f"CGPA {s.cgpa} below required {j.min_cgpa}.")
    if db.query(models.Application).filter(models.Application.student_id == s.id, models.Application.job_id == payload.job_id).first():
        raise HTTPException(status_code=400, detail="Already applied.")
    app = models.Application(student_id=s.id, job_id=payload.job_id, applied_on=date.today(), status="Applied")
    db.add(app); db.commit(); db.refresh(app)
    db.add(models.Notification(student_id=s.id, message=f"Applied to {j.title} at {j.company.name}. ✅", target="student"))
    db.add(models.Notification(student_id=None, message=f"{s.name} applied for {j.title}", target="admin"))
    db.commit()
    
    # Send Confirmation Email
    subject = f"Application Received: {j.title} at {j.company.name}"
    body = f"""
    <h2>Hello {s.name},</h2>
    <p>You have successfully applied for the position of <b>{j.title}</b> at <b>{j.company.name}</b>.</p>
    <p>We will notify you once the admin updates your status.</p>
    <br>
    <p>Best regards,<br>Unnati Career Portal Team</p>
    """
    trigger_email(bg, subject, s.email, body)

    return _app_q(db).filter(models.Application.id == app.id).first()

@router.get("/my", response_model=List[schemas.ApplicationOut])
def my_apps(current=Depends(require_student), db: Session = Depends(get_db)):
    return _app_q(db).filter(models.Application.student_id == current["id"]).order_by(models.Application.created_at.desc()).all()

@router.get("/", response_model=List[schemas.ApplicationOut])
def all_apps(
    job_id: Optional[int] = None, status: Optional[str] = None, course: Optional[str] = None,
    skip: int = 0, limit: int = 200,
    current=Depends(require_admin), db: Session = Depends(get_db)
):
    q = _app_q(db)
    if job_id: q = q.filter(models.Application.job_id == job_id)
    if status: q = q.filter(models.Application.status == status)
    if course: q = q.join(models.Student).filter(models.Student.course == course)
    return q.offset(skip).limit(limit).all()

@router.patch("/{aid}/status", response_model=schemas.ApplicationOut)
def update_status(aid: int, payload: schemas.ApplicationStatusUpdate, bg: BackgroundTasks, current=Depends(require_admin), db: Session = Depends(get_db)):
    valid = ["Applied", "Shortlisted", "Selected", "Rejected"]
    if payload.status not in valid:
        raise HTTPException(status_code=400, detail=f"Status must be one of {valid}")
    app = _app_q(db).filter(models.Application.id == aid).first()
    if not app: raise HTTPException(status_code=404, detail="Not found.")
    app.status = payload.status
    if payload.status == "Selected" and app.student:
        app.student.is_placed = True
    em = {"Selected": "🎊", "Shortlisted": "✅", "Rejected": "❌"}
    db.add(models.Notification(student_id=app.student_id, message=f"Your application for {app.job.title}: {payload.status} {em.get(payload.status, '')}", target="student"))
    db.commit(); db.refresh(app)

    # Send Status Update Email
    if app.student:
        subject = f"Application Update: {app.job.title}"
        status_color = {"Selected": "green", "Shortlisted": "blue", "Rejected": "red"}.get(payload.status, "black")
        body = f"""
        <h2>Hello {app.student.name},</h2>
        <p>There is an update on your application for <b>{app.job.title}</b> at <b>{app.job.company.name}</b>.</p>
        <p>Your new status is: <b style="color: {status_color};">{payload.status}</b></p>
        <br>
        <p>Log in to the portal for more details.</p>
        <p>Best regards,<br>Unnati Career Portal Team</p>
        """
        trigger_email(bg, subject, app.student.email, body)

    return app

@router.delete("/{aid}", response_model=schemas.MsgRes)
def del_app(aid: int, current=Depends(require_admin), db: Session = Depends(get_db)):
    app = db.query(models.Application).filter(models.Application.id == aid).first()
    if not app: raise HTTPException(status_code=404, detail="Not found.")
    db.delete(app); db.commit()
    return {"message": "Application deleted."}
