from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
import models, schemas
from auth_utils import require_admin

router = APIRouter()

@router.get("/", response_model=List[schemas.CompanyOut])
def list_companies(sector: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(models.Company)
    if sector: q = q.filter(models.Company.sector == sector)
    return q.all()

@router.get("/{cid}", response_model=schemas.CompanyOut)
def get_company(cid: int, db: Session = Depends(get_db)):
    c = db.query(models.Company).filter(models.Company.id == cid).first()
    if not c: raise HTTPException(status_code=404, detail="Not found.")
    return c

@router.post("/", response_model=schemas.CompanyOut, status_code=201)
def create_company(payload: schemas.CompanyCreate, current=Depends(require_admin), db: Session = Depends(get_db)):
    if db.query(models.Company).filter(models.Company.name == payload.name).first():
        raise HTTPException(status_code=400, detail="Company already exists.")
    c = models.Company(**payload.model_dump())
    db.add(c); db.commit(); db.refresh(c)
    return c

@router.put("/{cid}", response_model=schemas.CompanyOut)
def update_company(cid: int, payload: schemas.CompanyUpdate, current=Depends(require_admin), db: Session = Depends(get_db)):
    c = db.query(models.Company).filter(models.Company.id == cid).first()
    if not c: raise HTTPException(status_code=404, detail="Not found.")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(c, k, v)
    db.commit(); db.refresh(c)
    return c

@router.delete("/{cid}", response_model=schemas.MsgRes)
def del_company(cid: int, current=Depends(require_admin), db: Session = Depends(get_db)):
    c = db.query(models.Company).filter(models.Company.id == cid).first()
    if not c: raise HTTPException(status_code=404, detail="Not found.")
    n = db.query(models.Job).filter(models.Job.company_id == cid).count()
    if n: raise HTTPException(status_code=400, detail=f"Has {n} jobs. Delete jobs first.")
    db.delete(c); db.commit()
    return {"message": f"{c.name} deleted."}
