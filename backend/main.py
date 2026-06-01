"""
Unnati Career Portal Backend — main.py
FastAPI + MySQL
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn, os

from database import engine, Base
from routers import auth, students, companies, jobs, applications, notifications, stats, admin, external, scholarships

Base.metadata.create_all(bind=engine)
# Ensure profile_photo column exists
from sqlalchemy import text
with engine.connect() as conn:
    try:
        conn.execute(text("ALTER TABLE students ADD COLUMN profile_photo VARCHAR(200) AFTER is_placed"))
        conn.commit()
    except Exception:
        pass # Already exists or other error

# Ensure profile_photo column exists
from sqlalchemy import text
with engine.connect() as conn:
    try:
        conn.execute(text("ALTER TABLE students ADD COLUMN profile_photo VARCHAR(200) AFTER is_placed"))
        conn.commit()
    except Exception:
        pass # Already exists or other error


app = FastAPI(title="Unnati Career Portal API", version="1.0.0", docs_url="/docs")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("uploads/resumes", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(auth.router,          prefix="/api/auth",          tags=["Auth"])
app.include_router(students.router,      prefix="/api/students",      tags=["Students"])
app.include_router(companies.router,     prefix="/api/companies",     tags=["Companies"])
app.include_router(jobs.router,          prefix="/api/jobs",          tags=["Jobs"])
app.include_router(applications.router,  prefix="/api/applications",  tags=["Applications"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["Notifications"])
app.include_router(stats.router,         prefix="/api/stats",         tags=["Statistics"])
app.include_router(admin.router,         prefix="/api/admin",         tags=["Admin"])
app.include_router(external.router,      prefix="/api/external",      tags=["Insights"])
app.include_router(scholarships.router,  prefix="/api/scholarships",  tags=["Scholarships"])

# --- Health Check ---
@app.get("/health")
def health(): return {"status": "ok"}

# --- Redirects ---
from fastapi.responses import RedirectResponse
@app.get("/admin")
def admin_redirect():
    return RedirectResponse(url="/admin-login.html")

# --- Serve Frontend ---
# Use absolute path relative to this file for robustness
backend_dir = os.path.dirname(os.path.abspath(__file__))
frontend_path = os.path.join(os.path.dirname(backend_dir), "frontend")

if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
else:
    # Fallback for if we are running in a flat structure or other layouts
    if os.path.exists("frontend"):
        app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
