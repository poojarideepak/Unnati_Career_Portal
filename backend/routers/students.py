from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
import models, schemas
from auth_utils import require_student, require_admin
import shutil, os, uuid

router = APIRouter()
RESUME_DIR = "uploads/resumes"
PHOTO_DIR = "uploads/photos"
os.makedirs(RESUME_DIR, exist_ok=True)
os.makedirs(PHOTO_DIR, exist_ok=True)

@router.post("/me/photo", response_model=schemas.MsgRes)
def upload_photo(file: UploadFile = File(...), current=Depends(require_student), db: Session = Depends(get_db)):
    if not file.filename.lower().endswith((".jpg", ".jpeg", ".png")):
        raise HTTPException(status_code=400, detail="Only JPG and PNG files allowed.")
    s = current["user"]
    ext = file.filename.split(".")[-1]
    filename = f"{s.roll_no}_{uuid.uuid4().hex[:8]}.{ext}"
    with open(os.path.join(PHOTO_DIR, filename), "wb") as buf:
        shutil.copyfileobj(file.file, buf)
    s.profile_photo = filename
    db.commit()
    return {"message": f"Photo uploaded: {filename}"}

@router.get("/me", response_model=schemas.StudentOut)
def get_me(current=Depends(require_student)):
    return current["user"]

@router.put("/me", response_model=schemas.StudentOut)
def update_me(payload: schemas.StudentUpdate, current=Depends(require_student), db: Session = Depends(get_db)):
    s = current["user"]
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(s, k, v)
    db.commit(); db.refresh(s)
    return s

@router.post("/me/resume", response_model=schemas.MsgRes)
def upload_resume(file: UploadFile = File(...), current=Depends(require_student), db: Session = Depends(get_db)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files allowed.")
    s = current["user"]
    filename = f"{s.roll_no}_{uuid.uuid4().hex[:8]}.pdf"
    with open(os.path.join(RESUME_DIR, filename), "wb") as buf:
        shutil.copyfileobj(file.file, buf)
    s.resume = filename
    db.commit()
    return {"message": f"Resume uploaded: {filename}"}

@router.get("/", response_model=List[schemas.StudentOut])
def list_students(
    course: Optional[str] = None,
    search: Optional[str] = None,
    is_placed: Optional[bool] = None,
    skip: int = 0, limit: int = 100,
    current=Depends(require_admin), db: Session = Depends(get_db)
):
    q = db.query(models.Student)
    if course: q = q.filter(models.Student.course == course)
    if is_placed is not None: q = q.filter(models.Student.is_placed == is_placed)
    if search: q = q.filter(models.Student.name.ilike(f"%{search}%") | models.Student.roll_no.ilike(f"%{search}%"))
    return q.offset(skip).limit(limit).all()

@router.get("/{sid}", response_model=schemas.StudentOut)
def get_student(sid: int, current=Depends(require_admin), db: Session = Depends(get_db)):
    s = db.query(models.Student).filter(models.Student.id == sid).first()
    if not s: raise HTTPException(status_code=404, detail="Not found.")
    return s

@router.delete("/{sid}", response_model=schemas.MsgRes)
def del_student(sid: int, current=Depends(require_admin), db: Session = Depends(get_db)):
    s = db.query(models.Student).filter(models.Student.id == sid).first()
    if not s: raise HTTPException(status_code=404, detail="Not found.")
    db.delete(s); db.commit()
    return {"message": f"Student {s.name} deleted."}
