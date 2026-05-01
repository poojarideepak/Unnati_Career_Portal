from sqlalchemy import Column, Integer, String, Float, Boolean, Date, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Student(Base):
    __tablename__ = "students"
    id         = Column(Integer, primary_key=True, autoincrement=True)
    name       = Column(String(100), nullable=False)
    roll_no    = Column(String(20), unique=True, nullable=False, index=True)
    dob        = Column(String(12), nullable=False)   # DD-MM-YYYY = password
    email      = Column(String(100), unique=True, nullable=False)
    phone      = Column(String(20))
    course     = Column(String(20), nullable=False)
    cgpa       = Column(Float, nullable=False)
    skills     = Column(String(300))
    resume     = Column(String(200))
    batch      = Column(Integer, nullable=False)
    is_placed  = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    applications  = relationship("Application", back_populates="student", cascade="all,delete-orphan")
    notifications = relationship("Notification", back_populates="student", cascade="all,delete-orphan")


class Company(Base):
    __tablename__ = "companies"
    id         = Column(Integer, primary_key=True, autoincrement=True)
    name       = Column(String(100), unique=True, nullable=False)
    sector     = Column(String(30), nullable=False)
    pkg_range  = Column(String(50))
    roles      = Column(String(200))
    website    = Column(String(200))
    icon       = Column(String(10), default="🏢")
    rating     = Column(Float, default=4.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    jobs = relationship("Job", back_populates="company", cascade="all,delete-orphan")


class Job(Base):
    __tablename__ = "jobs"
    id          = Column(Integer, primary_key=True, autoincrement=True)
    company_id  = Column(Integer, ForeignKey("companies.id"), nullable=False)
    title       = Column(String(150), nullable=False)
    description = Column(Text)
    course      = Column(String(20), default="Any")
    min_cgpa    = Column(Float, default=0.0)
    skills      = Column(String(300))
    salary      = Column(String(30))
    drive_date  = Column(Date)
    is_active   = Column(Boolean, default=True)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())

    company      = relationship("Company", back_populates="jobs")
    applications = relationship("Application", back_populates="job", cascade="all,delete-orphan")


class Application(Base):
    __tablename__ = "applications"
    id         = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    job_id     = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    applied_on = Column(Date)
    status     = Column(String(20), default="Applied")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    student = relationship("Student", back_populates="applications")
    job     = relationship("Job", back_populates="applications")


class Notification(Base):
    __tablename__ = "notifications"
    id         = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=True)
    message    = Column(String(400), nullable=False)
    is_read    = Column(Boolean, default=False)
    target     = Column(String(20), default="student")   # student | admin
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("Student", back_populates="notifications")


class Alumni(Base):
    __tablename__ = "alumni"
    id          = Column(Integer, primary_key=True, autoincrement=True)
    name        = Column(String(100), nullable=False)
    batch       = Column(Integer, nullable=False)
    course      = Column(String(20), nullable=False)
    company     = Column(String(100))
    role        = Column(String(100))
    package     = Column(Float)
    email       = Column(String(100))
    achievement = Column(String(300))
    created_at  = Column(DateTime(timezone=True), server_default=func.now())



class InterviewForm(Base):
    __tablename__ = "interview_forms"
    id         = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    job_id     = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    form_url   = Column(String(500), nullable=False)
    note       = Column(String(300))
    is_active  = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Scholarship(Base):
    __tablename__ = "scholarships"
    id          = Column(Integer, primary_key=True, autoincrement=True)
    title       = Column(String(200), nullable=False)
    provider    = Column(String(200), nullable=False)
    amount      = Column(String(100))
    deadline    = Column(Date)
    description = Column(Text)
    eligibility = Column(String(300))
    apply_url   = Column(String(500))
    is_active   = Column(Boolean, default=True)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())
