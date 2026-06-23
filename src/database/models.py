from sqlalchemy import create_engine, Column, Integer, String, Text, Float, DateTime, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import os

# Base class for models
Base = declarative_base()

class User(Base):
    """User accounts"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    resumes = relationship("Resume", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(email='{self.email}', name='{self.name}')>"

class Resume(Base):
    """Uploaded resumes"""
    __tablename__ = 'resumes'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(Text)
    raw_text = Column(Text)
    extracted_skills = Column(JSON)  # Store as JSON array
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="resumes")
    analyses = relationship("Analysis", back_populates="resume", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Resume(file_name='{self.file_name}', user_id={self.user_id})>"

class JobDescription(Base):
    """Job postings for comparison"""
    __tablename__ = 'job_descriptions'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    company = Column(String(255))
    description_text = Column(Text, nullable=False)
    extracted_skills = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    analyses = relationship("Analysis", back_populates="job_description")
    
    def __repr__(self):
        return f"<JobDescription(title='{self.title}', company='{self.company}')>"

class Analysis(Base):
    """Skill gap analysis results"""
    __tablename__ = 'analyses'
    
    id = Column(Integer, primary_key=True)
    resume_id = Column(Integer, ForeignKey('resumes.id'), nullable=False)
    job_description_id = Column(Integer, ForeignKey('job_descriptions.id'), nullable=False)
    
    match_score = Column(Float)  # Percentage match
    matched_skills = Column(JSON)  # Array of matched skills
    missing_skills = Column(JSON)  # Array of gaps
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    resume = relationship("Resume", back_populates="analyses")
    job_description = relationship("JobDescription", back_populates="analyses")
    skill_gaps = relationship("SkillGap", back_populates="analysis", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Analysis(id={self.id}, match_score={self.match_score})>"

class SkillGap(Base):
    """Individual skill gaps with recommendations"""
    __tablename__ = 'skill_gaps'
    
    id = Column(Integer, primary_key=True)
    analysis_id = Column(Integer, ForeignKey('analyses.id'), nullable=False)
    
    skill_name = Column(String(255), nullable=False)
    skill_type = Column(String(100))  # Hard skill, Soft skill, etc.
    priority = Column(String(50))  # Critical, Important, Nice-to-have
    
    recommended_courses = Column(JSON)  # Array of course objects
    estimated_learning_time = Column(String(100))  # "2-3 months", etc.
    
    # Relationships
    analysis = relationship("Analysis", back_populates="skill_gaps")
    
    def __repr__(self):
        return f"<SkillGap(skill='{self.skill_name}', priority='{self.priority}')>"

# Database connection and session management
class Database:
    """Database connection handler"""
    
    def __init__(self, connection_string=None, use_sqlite=False):
        """
        Initialize database connection
        
        Args:
            connection_string: PostgreSQL connection string
            use_sqlite: If True, use SQLite for testing
        """
        if use_sqlite:
            connection_string = "sqlite:///skillgap_test.db"
        elif connection_string is None:
            # Use PostgreSQL for development
            connection_string = os.getenv(
                'DATABASE_URL',
                "postgresql://skillgap_user:your_password@localhost/skillgap_dev"
            )
        
        self.engine = create_engine(connection_string, echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    def create_tables(self):
        """Create all tables in the database"""
        Base.metadata.create_all(self.engine)
        print("All tables created successfully!")
    
    def drop_tables(self):
        """Drop all tables (use with caution!)"""
        Base.metadata.drop_all(self.engine)
        print("All tables dropped!")
    
    def get_session(self):
        """Get a new database session"""
        return self.SessionLocal()

# Example usage and testing
if __name__ == "__main__":
    # Initialize database
    db = Database()
    
    # Create tables
    db.create_tables()
    
    # Create a session
    session = db.get_session()
    
    try:
        # Create test user
        user = User(
            email="test@example.com",
            name="Test User"
        )
        session.add(user)
        session.commit()
        
        # Create test resume
        resume = Resume(
            user_id=user.id,
            file_name="test_resume.pdf",
            file_path="/data/raw/test_resume.pdf",
            raw_text="Sample resume text...",
            extracted_skills=["Python", "Machine Learning", "SQL"]
        )
        session.add(resume)
        session.commit()
        
        # Create test job description
        job = JobDescription(
            title="Machine Learning Engineer",
            company="Tech Corp",
            description_text="Looking for ML engineer with Python...",
            extracted_skills=["Python", "TensorFlow", "Machine Learning", "AWS"]
        )
        session.add(job)
        session.commit()
        
        # Create analysis
        analysis = Analysis(
            resume_id=resume.id,
            job_description_id=job.id,
            match_score=75.0,
            matched_skills=["Python", "Machine Learning"],
            missing_skills=["TensorFlow", "AWS"]
        )
        session.add(analysis)
        session.commit()
        
        # Create skill gaps
        gap1 = SkillGap(
            analysis_id=analysis.id,
            skill_name="TensorFlow",
            skill_type="Hard Skill",
            priority="Critical",
            recommended_courses=[
                {"name": "TensorFlow Developer Certificate", "platform": "Coursera"}
            ],
            estimated_learning_time="2-3 months"
        )
        gap2 = SkillGap(
            analysis_id=analysis.id,
            skill_name="AWS",
            skill_type="Hard Skill",
            priority="Important",
            recommended_courses=[
                {"name": "AWS Certified Solutions Architect", "platform": "AWS Training"}
            ],
            estimated_learning_time="3-4 months"
        )
        session.add_all([gap1, gap2])
        session.commit()
        
        print("\n=== Database Population Successful ===")
        print(f"User created: {user}")
        print(f"Resume created: {resume}")
        print(f"Job created: {job}")
        print(f"Analysis created: {analysis}")
        print(f"Skill gaps created: {gap1}, {gap2}")
        
        # Query example
        print("\n=== Query Test ===")
        all_users = session.query(User).all()
        print(f"Total users: {len(all_users)}")
        
        user_resumes = session.query(Resume).filter_by(user_id=user.id).all()
        print(f"User resumes: {len(user_resumes)}")
        
    except Exception as e:
        print(f"Error: {e}")
        session.rollback()
    finally:
        session.close()