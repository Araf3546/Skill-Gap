"""
Unified models — single Flask-SQLAlchemy registry (db.Model) for everything.
Do NOT create a second `db = SQLAlchemy()` anywhere else (e.g. app.py) —
import this one instead: `from src.database.models import db`.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, JSON, Boolean, Enum as SqlEnum
from datetime import datetime
import bcrypt
import enum

db = SQLAlchemy()


class Role(enum.Enum):
    USER = "user"
    ADMIN = "admin"


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    # Deterministic hash used only for lookup (not for security, just indexing)
    email_hash = Column(String(64), unique=True, nullable=False, index=True)
    # Encrypted actual PII — never stored in plaintext
    email_encrypted = Column(String(500), nullable=False)
    name_encrypted = Column(String(500), nullable=True)
    contact_encrypted = Column(String(500), nullable=True)

    password_hash = Column(String(255), nullable=False)  # bcrypt hash (salt built in)

    role = Column(SqlEnum(Role), default=Role.USER, nullable=False)

    totp_secret_encrypted = Column(String(500), nullable=True)  # 2FA secret, encrypted
    is_2fa_enabled = Column(Boolean, default=False)

    is_banned = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    # Relationships — the other side of each of these lives on the
    # respective model below, with a matching back_populates.
    resumes = db.relationship("Resume", back_populates="user", cascade="all, delete-orphan")
    resume_versions = db.relationship("ResumeVersion", back_populates="user", cascade="all, delete-orphan")
    skill_feedback = db.relationship("SkillFeedback", back_populates="user", cascade="all, delete-orphan")

    def set_password(self, plain_password: str):
        salt = bcrypt.gensalt(rounds=12)
        self.password_hash = bcrypt.hashpw(plain_password.encode(), salt).decode()

    def check_password(self, plain_password: str) -> bool:
        return bcrypt.checkpw(plain_password.encode(), self.password_hash.encode())

    def is_admin(self) -> bool:
        return self.role == Role.ADMIN

    def __repr__(self):
        return f"<User id={self.id} role={self.role.value}>"


class Resume(db.Model):
    """Uploaded resumes"""
    __tablename__ = 'resumes'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(Text)
    raw_text = Column(Text)
    extracted_skills = Column(JSON)  # Store as JSON array
    created_at = Column(DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="resumes")
    analyses = db.relationship("Analysis", back_populates="resume", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Resume(file_name='{self.file_name}', user_id={self.user_id})>"


class JobDescription(db.Model):
    """Job postings for comparison"""
    __tablename__ = 'job_descriptions'

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    company = Column(String(255))
    description_text = Column(Text, nullable=False)
    extracted_skills = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    analyses = db.relationship("Analysis", back_populates="job_description")

    def __repr__(self):
        return f"<JobDescription(title='{self.title}', company='{self.company}')>"


class Analysis(db.Model):
    """Skill gap analysis results"""
    __tablename__ = 'analyses'

    id = Column(Integer, primary_key=True)
    resume_id = Column(Integer, ForeignKey('resumes.id'), nullable=False)
    job_description_id = Column(Integer, ForeignKey('job_descriptions.id'), nullable=False)

    match_score = Column(Float)
    matched_skills = Column(JSON)
    missing_skills = Column(JSON)

    created_at = Column(DateTime, default=datetime.utcnow)

    resume = db.relationship("Resume", back_populates="analyses")
    job_description = db.relationship("JobDescription", back_populates="analyses")
    skill_gaps = db.relationship("SkillGap", back_populates="analysis", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Analysis(id={self.id}, match_score={self.match_score})>"


class SkillGap(db.Model):
    """Individual skill gaps with recommendations"""
    __tablename__ = 'skill_gaps'

    id = Column(Integer, primary_key=True)
    analysis_id = Column(Integer, ForeignKey('analyses.id'), nullable=False)

    skill_name = Column(String(255), nullable=False)
    skill_type = Column(String(100))
    priority = Column(String(50))

    recommended_courses = Column(JSON)
    estimated_learning_time = Column(String(100))

    analysis = db.relationship("Analysis", back_populates="skill_gaps")

    def __repr__(self):
        return f"<SkillGap(skill='{self.skill_name}', priority='{self.priority}')>"


class ResumeVersion(db.Model):
    """Resume version history (Day 14 — option 2)"""
    __tablename__ = 'resume_versions'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    version_number = Column(Integer, nullable=False)
    file_name = Column(String(255), nullable=False)
    extracted_skills = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="resume_versions")
    feedback_entries = db.relationship("SkillFeedback", back_populates="resume_version", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ResumeVersion(user_id={self.user_id}, v{self.version_number})>"


class SkillFeedback(db.Model):
    """Skill extraction correctness feedback (Day 15 — option 3)"""
    __tablename__ = 'skill_feedback'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    resume_version_id = Column(Integer, ForeignKey('resume_versions.id'), nullable=False)
    skill_name = Column(String(100), nullable=False)
    is_correct = Column(Boolean, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="skill_feedback")
    resume_version = db.relationship("ResumeVersion", back_populates="feedback_entries")

    def __repr__(self):
        return f"<SkillFeedback(skill='{self.skill_name}', correct={self.is_correct})>"