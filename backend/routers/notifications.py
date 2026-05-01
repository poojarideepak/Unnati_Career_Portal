from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from typing import List, Optional
from database import get_db
import models, schemas
from auth_utils import require_student, require_admin

# ── NOTIFICATIONS ──────────────────────────────────────
router = APIRouter()

@router.get("/my", response_model=List[schemas.NotifOut])
def my_notifs(current=Depends(require_student), db: Session = Depends(get_db)):
    return db.query(models.Notification).filter(models.Notification.student_id == current["id"]).order_by(models.Notification.created_at.desc()).limit(20).all()

@router.post("/my/read-all", response_model=schemas.MsgRes)
def read_all(current=Depends(require_student), db: Session = Depends(get_db)):
    db.query(models.Notification).filter(models.Notification.student_id == current["id"], models.Notification.is_read == False).update({"is_read": True})
    db.commit()
    return {"message": "Marked as read."}

@router.get("/admin", response_model=List[schemas.NotifOut])
def admin_notifs(current=Depends(require_admin), db: Session = Depends(get_db)):
    return db.query(models.Notification).filter(models.Notification.target == "admin").order_by(models.Notification.created_at.desc()).limit(30).all()
