"""
seed.py — Run once to populate database with sample data
Usage: python seed.py
"""
from database import SessionLocal, engine, Base
import models
from datetime import date

Base.metadata.create_all(bind=engine)
db = SessionLocal()

def seed():
    print("[INFO] Seeding Unnati Career Portal database...")

    cos = [
        models.Company(name="Infosys BPM",    sector="IT",         pkg_range="4–7 LPA",   roles="Analyst, Trainee",        website="https://infosys.com",   icon="💻", rating=4.2),
        models.Company(name="TCS Campus",     sector="IT",         pkg_range="3.5–6 LPA", roles="Systems Engineer, Exec",  website="https://tcs.com",       icon="🖥️", rating=4.0),
        models.Company(name="Deloitte India", sector="Consulting", pkg_range="5–12 LPA",  roles="Analyst, Consultant",     website="https://deloitte.com",  icon="📊", rating=4.8),
        models.Company(name="HDFC Bank",      sector="Finance",    pkg_range="3–6 LPA",   roles="RM, Branch Officer",      website="https://hdfcbank.com",  icon="🏦", rating=3.9),
        models.Company(name="KPMG",           sector="Finance",    pkg_range="5–10 LPA",  roles="Audit, Tax, Advisory",    website="https://kpmg.com",      icon="📋", rating=4.5),
    ]
    for c in cos:
        if not db.query(models.Company).filter(models.Company.name == c.name).first():
            db.add(c)
    db.commit()
    c1,c2,c3,c4,c5 = [db.query(models.Company).filter(models.Company.name == c.name).first() for c in cos]
    print("  [OK] Companies seeded")

    stus = [
        models.Student(name="Aarav Sharma", roll_no="22BBA101", dob="15-08-2002", email="aarav@college.edu", phone="+91 9876543210", course="BBA",   cgpa=8.2, skills="Marketing, Excel, Tally",    batch=2025, is_placed=False),
        models.Student(name="Priya Nair",   roll_no="22COM205", dob="22-03-2002", email="priya@college.edu", phone="+91 9988776655", course="B.Com", cgpa=7.8, skills="Accounting, GST, Tally",     batch=2025, is_placed=False),
        models.Student(name="Rohit Verma",  roll_no="22VOC310", dob="10-11-2001", email="rohit@college.edu", phone="+91 9123456789", course="BCA", cgpa=6.5, skills="Java, Python, SQL",          batch=2025, is_placed=False),
        models.Student(name="Sneha Patel",  roll_no="22BBA102", dob="05-07-2002", email="sneha@college.edu", phone="+91 9871234560", course="BBA",   cgpa=9.1, skills="Finance, Excel, PowerBI",    batch=2025, is_placed=True),
        models.Student(name="Kiran Joshi",  roll_no="22COM301", dob="18-01-2002", email="kiran@college.edu", phone="+91 9001234567", course="B.Com", cgpa=8.6, skills="Audit, Tally, Excel",        batch=2025, is_placed=True),
    ]
    for s in stus:
        if not db.query(models.Student).filter(models.Student.roll_no == s.roll_no).first():
            db.add(s)
    db.commit()
    s1,s2,s3,s4,s5 = [db.query(models.Student).filter(models.Student.roll_no == s.roll_no).first() for s in stus]
    print("  [OK] Students seeded")

    jobs = [
        models.Job(company_id=c1.id, title="Business Analyst",       description="Analyse business processes and improve efficiency using data.", course="BBA",   min_cgpa=7.0, skills="Excel, PowerBI", salary="5.5 LPA", drive_date=date(2026,4,10)),
        models.Job(company_id=c2.id, title="Accounts Executive",      description="Handle GST filing, accounts reconciliation and payroll.",       course="B.Com", min_cgpa=6.5, skills="Tally, GST",    salary="3.8 LPA", drive_date=date(2026,4,14)),
        models.Job(company_id=c3.id, title="Finance Analyst Trainee", description="Support finance team with reporting and data analysis.",         course="Any",   min_cgpa=7.5, skills="Finance, Excel", salary="6.0 LPA", drive_date=date(2026,4,18)),
        models.Job(company_id=c1.id, title="HR Associate",            description="Assist with campus recruitment and onboarding.",                 course="BBA",   min_cgpa=6.0, skills="Communication",  salary="4.0 LPA", drive_date=date(2026,4,20)),
        models.Job(company_id=c2.id, title="Systems Trainee",         description="Work on internal ERP and provide Level-1 support.",             course="BCA", min_cgpa=6.0, skills="Java, SQL",      salary="4.5 LPA", drive_date=date(2026,4,22)),
    ]
    added_jobs = []
    for j in jobs:
        ex = db.query(models.Job).filter(models.Job.title == j.title, models.Job.company_id == j.company_id).first()
        if not ex: db.add(j); db.flush(); added_jobs.append(j)
        else: added_jobs.append(ex)
    db.commit()
    j1,j2,j3,j4,j5 = [db.query(models.Job).filter(models.Job.title == j.title, models.Job.company_id == j.company_id).first() for j in jobs]
    print("  [OK] Jobs seeded")

    apps = [
        (s1.id, j1.id, date(2026,4,2), "Shortlisted"),
        (s2.id, j2.id, date(2026,4,3), "Applied"),
        (s3.id, j5.id, date(2026,4,4), "Rejected"),
        (s4.id, j3.id, date(2026,4,1), "Selected"),
        (s5.id, j3.id, date(2026,4,2), "Selected"),
    ]
    for sid,jid,dt,st in apps:
        if not db.query(models.Application).filter(models.Application.student_id==sid, models.Application.job_id==jid).first():
            db.add(models.Application(student_id=sid, job_id=jid, applied_on=dt, status=st))
    db.commit()
    print("  [OK] Applications seeded")

    alumni = [
        models.Alumni(name="Arun Nair",       batch=2019, course="BBA",   company="EY India",        role="Director – Advisory",   package=35.0,  achievement="Youngest Director in batch 🏅"),
        models.Alumni(name="Suresh Babu",     batch=2020, course="BBA",   company="Google India",    role="Business Dev Manager",  package=28.0,  achievement="MBA from IIM-A, now at Google 🎉"),
        models.Alumni(name="Pooja Mehta",     batch=2020, course="B.Com", company="Deloitte India",  role="Senior Consultant",     package=20.0,  achievement="5 promotions in 3 years 🚀"),
        models.Alumni(name="Vikram Joshi",    batch=2021, course="B.Com", company="PwC",             role="Manager – Audit",       package=18.0,  achievement="Cleared CA Final while working 🍎"),
        models.Alumni(name="Ravi Shankar",    batch=2021, course="BCA", company="Microsoft India", role="Developer",             package=16.5,  achievement="Cleared GATE 2022, joined Microsoft"),
        models.Alumni(name="Ananya Krishnan", batch=2022, course="BBA",   company="Amazon India",    role="Senior Analyst",        package=14.0,  achievement="Promoted to Senior in 2 years 🥇"),
        models.Alumni(name="Meera Iyer",      batch=2022, course="B.Com", company="ICICI Bank",      role="Branch Manager",        package=12.5,  achievement="Top performer award 2024 ⭐"),
        models.Alumni(name="Lakshmi Rao",     batch=2023, course="B.Com", company="McKinsey",        role="Consultant",            package=22.0,  achievement="Joined as first batch MBA ⭐"),
    ]
    for a in alumni:
        if not db.query(models.Alumni).filter(models.Alumni.name == a.name).first():
            db.add(a)
    db.commit()
    print("  [OK] Alumni seeded")

    forms = [
        models.InterviewForm(company_id=c1.id, job_id=j1.id, form_url="https://forms.google.com/infosys-ba",    note="Fill before the drive date. Bring a printout."),
        models.InterviewForm(company_id=c3.id, job_id=j3.id, form_url="https://forms.google.com/deloitte-fa",   note="Upload latest resume inside the form."),
    ]
    for f in forms:
        if not db.query(models.InterviewForm).filter(models.InterviewForm.job_id == f.job_id).first():
            db.add(f)
    db.commit()
    print("  [OK] Interview forms seeded")

    scholarships = [
        models.Scholarship(title="Merit-cum-Means Scholarship", provider="College Alumni Association", amount="₹50,000", deadline=date(2026,6,15), description="Scholarship for meritorious students from economically weaker sections.", eligibility="CGPA > 8.0, Family income < 5LPA", apply_url="https://college.edu/scholarships/mcm"),
        models.Scholarship(title="Tech Innovation Award", provider="Digital India Foundation", amount="₹1,00,000", deadline=date(2026,7,20), description="For students with outstanding projects in software or hardware innovation.", eligibility="BCA students with 7.5+ CGPA", apply_url="https://digitalindia.gov.in/awards"),
        models.Scholarship(title="Women in Finance Leadership", provider="HDFC Bank CSR", amount="₹75,000", deadline=date(2026,5,30), description="Empowering female students pursuing careers in banking and finance.", eligibility="Female students, B.Com/BBA, 7.0+ CGPA", apply_url="https://hdfcbank.com/csr/women-finance"),
    ]
    for s in scholarships:
        if not db.query(models.Scholarship).filter(models.Scholarship.title == s.title).first():
            db.add(s)
    db.commit()
    print("  [OK] Scholarships seeded")

    print("\n[SUCCESS] Seeding complete!")
    print("   Admin:   admin@unnati.com / admin123")
    print("   Student: Roll=22BBA101 / DOB=15-08-2002")

if __name__ == "__main__":
    seed()
    db.close()
