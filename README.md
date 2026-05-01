# Unnati Career Portal — Full Stack Setup Guide
## FastAPI Backend + HTML/JS Frontend

---

## 📁 Project Structure

```
placeit_full/
│
├── backend/                    ← Python FastAPI backend
│   ├── main.py                 ← App entry point
│   ├── database.py             ← MySQL connection
│   ├── models.py               ← Database tables
│   ├── schemas.py              ← Request/Response models
│   ├── auth_utils.py           ← JWT authentication
│   ├── config.py               ← Settings (.env loader)
│   ├── seed.py                 ← Insert sample data
│   ├── requirements.txt        ← Python packages
│   ├── .env                    ← Your database config
│   └── routers/
│       ├── auth.py             ← Login / Register
│       ├── students.py         ← Student endpoints
│       ├── companies.py        ← Company endpoints
│       ├── jobs.py             ← Job drive endpoints
│       ├── applications.py     ← Application endpoints
│       ├── notifications.py    ← Notification endpoints
│       ├── stats.py            ← Statistics endpoints
│       └── admin.py            ← Admin dashboard + forms
│
└── frontend/                   ← HTML frontend pages
    ├── api.js                  ← API helper (all fetch calls)
    ├── index.html              ← Public guest stats page
    ├── student-login.html      ← Student login & register
    ├── admin-login.html        ← Admin login
    └── app.html                ← Main dashboard (student+admin)
```

---

## ⚙️ STEP-BY-STEP SETUP

### STEP 1 — MySQL Setup
```sql
CREATE DATABASE placeit_db;
```

### STEP 2 — Configure .env
Edit `backend/.env`:
```
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=YOUR_MYSQL_PASSWORD
DB_NAME=placeit_db
SECRET_KEY=placeit_super_secret_key_2026
ADMIN_EMAIL=admin@unnati.com
ADMIN_PASSWORD=admin123
```

### STEP 3 — Install Python packages
```bash
cd backend
python -m venv venv

# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### STEP 4 — Start the backend
```bash
python main.py
```
Backend runs at: http://localhost:8000
API Docs:        http://localhost:8000/docs

### STEP 5 — Seed sample data
```bash
python seed.py
```

### STEP 6 — Open the frontend
Open `frontend/index.html` in your browser.

> ⚠️ All 4 frontend files must stay in the SAME folder.
> The `api.js` file must be in the same folder as the HTML files.

---

## 🔐 Login Credentials

| Role    | Username/Email       | Password      |
|---------|----------------------|---------------|
| Student | 22BBA101 (Roll No)   | 15-08-2002    |
| Student | 22COM205 (Roll No)   | 22-03-2002    |
| Student | 22VOC310 (Roll No)   | 10-11-2001    |
| Admin   | admin@unnati.com    | admin123      |

---

## 🔗 How It Works (Flow)

```
index.html (public — stats from /api/stats/overview)
  ├── Student Login → student-login.html
  │     └── POST /api/auth/student/login
  │           └── token saved → redirect to app.html
  └── Admin Login → admin-login.html
        └── POST /api/auth/admin/login
              └── token saved → redirect to app.html

app.html (protected)
  ├── GET /api/students/me          ← student profile
  ├── GET /api/jobs/                ← browse jobs
  ├── POST /api/applications/       ← apply for job
  ├── GET /api/applications/my      ← my applications
  ├── GET /api/notifications/my     ← student notifications
  ├── GET /api/admin/dashboard      ← admin dashboard
  ├── GET /api/students/            ← admin: all students
  ├── GET /api/jobs/all             ← admin: all jobs
  ├── GET /api/applications/        ← admin: all applicants
  ├── PATCH /api/applications/{id}/status ← shortlist/select/reject
  ├── GET /api/companies/           ← companies list
  ├── POST /api/companies/          ← admin: add company
  ├── GET /api/admin/interview-forms ← interview forms
  └── GET /api/stats/overview       ← placement stats
```

---

## 📡 All API Endpoints

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/auth/student/login | Roll No + DOB login |
| POST | /api/auth/admin/login | Admin login |
| POST | /api/auth/student/register | New student register |

### Students
| Method | Endpoint | Auth |
|--------|----------|------|
| GET | /api/students/me | Student |
| PUT | /api/students/me | Student |
| POST | /api/students/me/resume | Student |
| GET | /api/students/ | Admin |
| DELETE | /api/students/{id} | Admin |

### Jobs
| Method | Endpoint | Auth |
|--------|----------|------|
| GET | /api/jobs/ | Public |
| GET | /api/jobs/all | Admin |
| POST | /api/jobs/ | Admin |
| PUT | /api/jobs/{id} | Admin |
| DELETE | /api/jobs/{id} | Admin |

### Applications
| Method | Endpoint | Auth |
|--------|----------|------|
| POST | /api/applications/ | Student |
| GET | /api/applications/my | Student |
| GET | /api/applications/ | Admin |
| PATCH | /api/applications/{id}/status | Admin |

### Stats (Public)
| Method | Endpoint | Auth |
|--------|----------|------|
| GET | /api/stats/overview | Public |
| GET | /api/stats/placed-students | Public |
| GET | /api/stats/alumni | Public |

---
*Unnati Career Portal Full Stack v1.0*
