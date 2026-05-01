from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import get_db
from config import settings
import models

security = HTTPBearer()

def create_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode["exp"] = expire
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token invalid or expired.")

def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    payload = decode_token(creds.credentials)
    role    = payload.get("role")
    sub     = payload.get("sub")
    if not role or not sub:
        raise HTTPException(status_code=401, detail="Invalid token.")
    if role == "student":
        student = db.query(models.Student).filter(models.Student.id == int(sub)).first()
        if not student:
            raise HTTPException(status_code=401, detail="Student not found.")
        return {"role": "student", "user": student, "id": student.id}
    elif role == "admin":
        return {"role": "admin", "user": None, "id": 0}
    raise HTTPException(status_code=401, detail="Unknown role.")

def require_student(current=Depends(get_current_user)):
    if current["role"] != "student":
        raise HTTPException(status_code=403, detail="Students only.")
    return current

def require_admin(current=Depends(get_current_user)):
    if current["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only.")
    return current
