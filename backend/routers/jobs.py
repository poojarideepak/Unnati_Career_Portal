from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from database import get_db
import models, schemas
from auth_utils import require_admin
from email_utils import trigger_email
from fastapi import BackgroundTasks

router = APIRouter()

def _job_q(db): return db.query(models.Job).options(joinedload(models.Job.company))

@router.get("/", response_model=List[schemas.JobOut])
def list_jobs(course: Optional[str] = None, search: Optional[str] = None, db: Session = Depends(get_db)):
    q = _job_q(db).filter(models.Job.is_active == True)
    if course and course != "Any":
        q = q.filter((models.Job.course == course) | (models.Job.course == "Any"))
    if search: q = q.filter(models.Job.title.ilike(f"%{search}%"))
    return q.order_by(models.Job.drive_date).all()

@router.get("/all", response_model=List[schemas.JobOut])
def list_all_jobs(current=Depends(require_admin), db: Session = Depends(get_db)):
    return _job_q(db).all()

@router.get("/{jid}", response_model=schemas.JobOut)
def get_job(jid: int, db: Session = Depends(get_db)):
    j = _job_q(db).filter(models.Job.id == jid).first()
    if not j: raise HTTPException(status_code=404, detail="Not found.")
    return j

@router.post("/", response_model=schemas.JobOut, status_code=201)
def create_job(payload: schemas.JobCreate, bg: BackgroundTasks, current=Depends(require_admin), db: Session = Depends(get_db)):
    co = db.query(models.Company).filter(models.Company.id == payload.company_id).first()
    if not co: raise HTTPException(status_code=404, detail="Company not found.")
    j = models.Job(**payload.model_dump())
    db.add(j); db.commit(); db.refresh(j)
    for s in db.query(models.Student).all():
        db.add(models.Notification(student_id=s.id, message=f"New job: {j.title} at {co.name} 📋", target="student"))
        
        # Email Notification
        subject = f"New Job Opportunity: {j.title} at {co.name}"
        body = f"<h2>Hello {s.name},</h2><p>A new job opportunity has been posted!</p><p><b>Role:</b> {j.title}<br><b>Company:</b> {co.name}</p><p>Log in to your dashboard to view more details and apply.</p><br><p>Best,<br>Placement Cell</p>"
        trigger_email(bg, subject, s.email, body)
        
    db.commit()
    return _job_q(db).filter(models.Job.id == j.id).first()

@router.put("/{jid}", response_model=schemas.JobOut)
def update_job(jid: int, payload: schemas.JobUpdate, current=Depends(require_admin), db: Session = Depends(get_db)):
    j = db.query(models.Job).filter(models.Job.id == jid).first()
    if not j: raise HTTPException(status_code=404, detail="Not found.")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(j, k, v)
    db.commit()
    return _job_q(db).filter(models.Job.id == jid).first()

@router.delete("/{jid}", response_model=schemas.MsgRes)
def del_job(jid: int, current=Depends(require_admin), db: Session = Depends(get_db)):
    j = db.query(models.Job).filter(models.Job.id == jid).first()
    if not j: raise HTTPException(status_code=404, detail="Not found.")
    db.delete(j); db.commit()
    return {"message": f"Job {j.title} deleted."}
