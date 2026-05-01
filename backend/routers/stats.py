from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from typing import List, Optional
from database import get_db
import models, schemas
from auth_utils import require_admin, require_student

router = APIRouter()

@router.get("/predict")
def predict_placement(current=Depends(require_student), db: Session = Depends(get_db)):
    s = current["user"]
    # Simple heuristic prediction logic
    # Score 0-100
    score = 0
    
    # 1. CGPA (Max 40 points)
    score += (s.cgpa / 10.0) * 40
    
    # 2. Skills count (Max 30 points)
    skills = [sk.strip() for sk in (s.skills or "").split(",") if sk.strip()]
    score += min(len(skills) * 5, 30)
    
    # 3. Application count (Max 15 points)
    apps_count = db.query(models.Application).filter(models.Application.student_id == s.id).count()
    score += min(apps_count * 3, 15)
    
    # 4. Shortlist history (Max 15 points)
    shortlisted = db.query(models.Application).filter(models.Application.student_id == s.id, models.Application.status == "Shortlisted").count()
    score += min(shortlisted * 5, 15)
    
    # Recommendations
    recs = []
    if s.cgpa < 8.0: recs.append("Maintain a CGPA above 8.0 for top tier companies.")
    if len(skills) < 4: recs.append("Add more technical skills to your profile.")
    if apps_count < 3: recs.append("Apply to at least 5 job drives to increase chances.")
    if not shortlisted and apps_count > 0: recs.append("Your skills might not match the jobs you applied for. Review requirements.")

    return {
        "probability": round(score, 1),
        "status": "High" if score > 75 else "Medium" if score > 50 else "Improving",
        "recommendations": recs,
        "breakdown": {
            "Academic": round((s.cgpa/10)*40, 1),
            "Skills": min(len(skills)*5, 30),
            "Engagement": min(apps_count*3 + shortlisted*5, 30)
        }
    }

def _parse_pkg(salary_str):
    try: return float(str(salary_str).replace(" LPA","").replace("LPA","").strip())
    except: return 0.0

@router.get("/overview")
def overview(db: Session = Depends(get_db)):
    total     = db.query(models.Student).count()
    placed    = db.query(models.Student).filter(models.Student.is_placed == True).count()
    companies = db.query(models.Company).count()
    jobs      = db.query(models.Job).filter(models.Job.is_active == True).count()
    apps      = db.query(models.Application).count()
    alumni_ct = db.query(models.Alumni).count()

    sel = db.query(models.Application, models.Job).join(models.Job).filter(models.Application.status == "Selected").all()
    pkgs = [_parse_pkg(j.salary) for _, j in sel if j.salary]
    al_recs = db.query(models.Alumni).all()
    al_pkgs = [a.package for a in al_recs if a.package]
    all_pkgs = pkgs + al_pkgs

    avg_pkg     = round(sum(pkgs)/len(pkgs), 2) if pkgs else 0.0
    highest_pkg = round(max(all_pkgs), 2) if all_pkgs else 0.0

    # ── BRANCH STATS ───────────────────────────────────
    byBranch = []
    for c in ["B.Com","BBA","BCA"]:
        t = db.query(models.Student).filter(models.Student.course == c).count()
        p = db.query(models.Student).filter(models.Student.course == c, models.Student.is_placed == True).count()
        if t: byBranch.append({"course": c, "total": t, "placed": p, "rate": round(p/t*100,1)})

    # ── YEAR-WISE PLACEMENTS ───────────────────────────
    # Combine students and alumni to get a timeline
    year_data = {}
    for a in al_recs:
        year_data[a.batch] = year_data.get(a.batch, 0) + 1
    
    # Current batch (assume 2025 for now based on seed)
    curr_placed = db.query(models.Student).filter(models.Student.is_placed == True).count()
    year_data[2025] = curr_placed

    years = sorted(year_data.keys())
    yearly_placements = [{"year": y, "count": year_data[y]} for y in years]

    # ── PACKAGE DISTRIBUTION ───────────────────────────
    ranges = {"0-3": 0, "3-6": 0, "6-9": 0, "9-12": 0, "12+": 0}
    for p in all_pkgs:
        if p < 3: ranges["0-3"] += 1
        elif p < 6: ranges["3-6"] += 1
        elif p < 9: ranges["6-9"] += 1
        elif p < 12: ranges["9-12"] += 1
        else: ranges["12+"] += 1
    pkg_dist = [{"range": k, "count": v} for k, v in ranges.items()]

    # ── TOP RECRUITERS ────────────────────────────────
    top_cos = db.query(models.Company.name, func.count(models.Job.id).label("job_count"))\
        .join(models.Job).group_by(models.Company.name).order_by(func.count(models.Job.id).desc()).limit(6).all()
    top_recruiters = [{"name": c.name, "count": c.job_count} for c in top_cos]

    # ── TREND ─────────────────────────────────────────
    # Average package by year
    trend_data = {}
    for a in al_recs:
        if a.package:
            trend_data.setdefault(a.batch, []).append(a.package)
    if pkgs:
        trend_data.setdefault(2025, []).extend(pkgs)
    
    trend = [{"year": y, "avg": round(sum(trend_data[y])/len(trend_data[y]), 2)} for y in sorted(trend_data.keys())]

    return {
        "total_students": total, "placed": placed, "unplaced": total-placed,
        "placement_rate": round(placed/total*100,1) if total else 0.0,
        "companies": companies, "jobs": jobs, "applications": apps,
        "alumni": alumni_ct, "all_time_placed": placed+alumni_ct,
        "avg_package": avg_pkg, "highest_package": highest_pkg,
        "branch_stats": byBranch,
        "yearly_placements": yearly_placements,
        "package_distribution": pkg_dist,
        "top_recruiters": top_recruiters,
        "trend": trend
    }

@router.get("/placed-students", response_model=List[schemas.StudentPublic])
def placed_students(db: Session = Depends(get_db)):
    return db.query(models.Student).filter(models.Student.is_placed == True).all()

@router.get("/alumni", response_model=List[schemas.AlumniOut])
def get_alumni(batch: Optional[int] = None, db: Session = Depends(get_db)):
    q = db.query(models.Alumni)
    if batch: q = q.filter(models.Alumni.batch == batch)
    return q.order_by(models.Alumni.batch.desc()).all()

@router.post("/alumni", response_model=schemas.AlumniOut, status_code=201)
def add_alumni(payload: schemas.AlumniCreate, current=Depends(require_admin), db: Session = Depends(get_db)):
    a = models.Alumni(**payload.model_dump())
    db.add(a); db.commit(); db.refresh(a)
    return a

@router.delete("/alumni/{aid}", response_model=schemas.MsgRes)
def del_alumni(aid: int, current=Depends(require_admin), db: Session = Depends(get_db)):
    a = db.query(models.Alumni).filter(models.Alumni.id == aid).first()
    if not a: raise HTTPException(status_code=404, detail="Not found.")
    db.delete(a); db.commit()
    return {"message": "Alumni deleted."}
