from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from database import get_db
import models, schemas
from auth_utils import require_admin
from email_utils import trigger_email

router = APIRouter()

@router.post("/broadcast", response_model=schemas.MsgRes)
def broadcast(payload: schemas.BroadcastReq, bg: BackgroundTasks, current=Depends(require_admin), db: Session = Depends(get_db)):
    q = db.query(models.Student)
    if payload.course:
        q = q.filter(models.Student.course == payload.course)
    
    students = q.all()
    for s in students:
        # In-app notification
        db.add(models.Notification(student_id=s.id, message=f"📢 {payload.message}", target="student"))
        
        # Email notification
        subject = "📢 Important Announcement from Placement Cell"
        body = f"""
        <h2>Important Announcement</h2>
        <p>{payload.message}</p>
        <br>
        <p>Regards,<br>Placement Cell Team</p>
        """
        trigger_email(bg, subject, s.email, body)
        
    db.commit()
    return {"message": f"Broadcast sent to {len(students)} students."}

@router.get("/dashboard")
def dashboard(current=Depends(require_admin), db: Session = Depends(get_db)):
    placed  = db.query(models.Student).filter(models.Student.is_placed==True).count()
    total   = db.query(models.Student).count()
    return {
        "stats": {
            "total_students": total, "placed": placed, "unplaced": total-placed,
            "companies": db.query(models.Company).count(),
            "jobs": db.query(models.Job).count(),
            "applications": db.query(models.Application).count(),
            "shortlisted": db.query(models.Application).filter(models.Application.status=="Shortlisted").count(),
            "selected": db.query(models.Application).filter(models.Application.status=="Selected").count(),
        },
        "recent_placements": [
            {"student": a.student.name if a.student else "—", "job": a.job.title if a.job else "—",
             "company": a.job.company.name if (a.job and a.job.company) else "—", "salary": a.job.salary if a.job else "—"}
            for a in db.query(models.Application).options(joinedload(models.Application.student), joinedload(models.Application.job).joinedload(models.Job.company))
                .filter(models.Application.status=="Selected").limit(5).all()
        ],
        "recent_applications": [
            {"student": a.student.name if a.student else "—", "job": a.job.title if a.job else "—", "status": a.status, "date": str(a.applied_on)}
            for a in db.query(models.Application).options(joinedload(models.Application.student), joinedload(models.Application.job))
                .order_by(models.Application.created_at.desc()).limit(6).all()
        ]
    }

# ── INTERVIEW FORMS ────────────────────────────────────
@router.get("/interview-forms", response_model=List[schemas.IFormOut])
def list_forms(db: Session = Depends(get_db)):
    return db.query(models.InterviewForm).filter(models.InterviewForm.is_active == True).all()

@router.post("/interview-forms", response_model=schemas.IFormOut, status_code=201)
def create_form(payload: schemas.IFormCreate, bg: BackgroundTasks, current=Depends(require_admin), db: Session = Depends(get_db)):
    f = models.InterviewForm(**payload.model_dump())
    db.add(f); db.commit(); db.refresh(f)
    for s in db.query(models.Student).all():
        j = db.query(models.Job).filter(models.Job.id == payload.job_id).first()
        co = db.query(models.Company).filter(models.Company.id == payload.company_id).first()
        db.add(models.Notification(student_id=s.id, message=f"Interview form available for {j.title if j else 'a job'} — check Interview Forms tab! 📝", target="student"))
        
        # Email Notification
        subject = f"Interview Form: {j.title if j else 'A Job'} at {co.name if co else 'a Company'}"
        body = f"<h2>Hello {s.name},</h2><p>A new interview form is available for you to fill out.</p><p>Please log in to your dashboard and check the 'Interview Forms' tab to access it.</p><br><p>Best,<br>Placement Cell</p>"
        trigger_email(bg, subject, s.email, body)
        
    db.commit()
    return f

@router.delete("/interview-forms/{fid}", response_model=schemas.MsgRes)
def del_form(fid: int, current=Depends(require_admin), db: Session = Depends(get_db)):
    f = db.query(models.InterviewForm).filter(models.InterviewForm.id == fid).first()
    if not f: raise HTTPException(status_code=404, detail="Not found.")
    db.delete(f); db.commit()
    return {"message": "Form deleted."}
