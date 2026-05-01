from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import Scholarship
from schemas import ScholarshipCreate, ScholarshipOut, MsgRes
from auth_utils import get_current_user

router = APIRouter()

@router.get("", response_model=List[ScholarshipOut])
def list_scholarships(db: Session = Depends(get_db)):
    """List all active scholarships."""
    return db.query(Scholarship).filter(Scholarship.is_active == True).all()

@router.post("", response_model=ScholarshipOut)
def create_scholarship(
    data: ScholarshipCreate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_user)
):
    """Admin only: Create a new scholarship."""
    if admin.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Only admins can manage scholarships")
    
    new_sch = Scholarship(**data.dict())
    db.add(new_sch)
    db.commit()
    db.refresh(new_sch)
    return new_sch

@router.delete("/{id}", response_model=MsgRes)
def delete_scholarship(
    id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_current_user)
):
    """Admin only: Delete a scholarship."""
    if admin.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Only admins can manage scholarships")
    
    sch = db.query(Scholarship).filter(Scholarship.id == id).first()
    if not sch:
        raise HTTPException(status_code=404, detail="Scholarship not found")
    
    db.delete(sch)
    db.commit()
    return {"message": "Scholarship deleted successfully", "success": True}
