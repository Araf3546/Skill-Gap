from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from .models import User, Resume, JobDescription, Analysis, SkillGap
import logging

logger = logging.getLogger(__name__)

class DatabaseOperations:
    """Handle all database CRUD operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    # ============ USER OPERATIONS ============
    
    def create_user(self, email: str, name: str = None) -> User:
        """Create a new user"""
        user = User(email=email, name=name)
        self.session.add(user)
        self.session.commit()
        logger.info(f"User created: {email}")
        return user
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Find user by email"""
        return self.session.query(User).filter_by(email=email).first()
    
    def get_or_create_user(self, email: str, name: str = None) -> User:
        """Get existing user or create new one"""
        user = self.get_user_by_email(email)
        if not user:
            user = self.create_user(email, name)
        return user
    
    # ============ RESUME OPERATIONS ============
    
    def create_resume(self, user_id: int, file_name: str, 
                     raw_text: str, extracted_skills: List[str]) -> Resume:
        """Save a resume to database"""
        resume = Resume(
            user_id=user_id,
            file_name=file_name,
            raw_text=raw_text,
            extracted_skills=extracted_skills
        )
        self.session.add(resume)
        self.session.commit()
        logger.info(f"Resume saved: {file_name}")
        return resume
    
    def get_resume(self, resume_id: int) -> Optional[Resume]:
        """Get resume by ID"""
        return self.session.query(Resume).filter_by(id=resume_id).first()
    
    def get_user_resumes(self, user_id: int) -> List[Resume]:
        """Get all resumes for a user"""
        return self.session.query(Resume).filter_by(user_id=user_id).all()
    
    # ============ JOB DESCRIPTION OPERATIONS ============
    
    def create_job_description(self, title: str, company: str,
                              description_text: str, 
                              extracted_skills: List[str]) -> JobDescription:
        """Save job description"""
        job = JobDescription(
            title=title,
            company=company,
            description_text=description_text,
            extracted_skills=extracted_skills
        )
        self.session.add(job)
        self.session.commit()
        logger.info(f"Job saved: {title} at {company}")
        return job
    
    def get_job_description(self, job_id: int) -> Optional[JobDescription]:
        """Get job by ID"""
        return self.session.query(JobDescription).filter_by(id=job_id).first()
    
    # ============ ANALYSIS OPERATIONS ============
    
    def create_analysis(self, resume_id: int, job_description_id: int,
                       match_score: float, matched_skills: List[str],
                       missing_skills: List[str]) -> Analysis:
        """Save analysis results"""
        analysis = Analysis(
            resume_id=resume_id,
            job_description_id=job_description_id,
            match_score=match_score,
            matched_skills=matched_skills,
            missing_skills=missing_skills
        )
        self.session.add(analysis)
        self.session.commit()
        logger.info(f"Analysis created: ID {analysis.id}")
        return analysis
    
    def get_analysis(self, analysis_id: int) -> Optional[Analysis]:
        """Get analysis by ID"""
        return self.session.query(Analysis).filter_by(id=analysis_id).first()
    
    def get_resume_analyses(self, resume_id: int) -> List[Analysis]:
        """Get all analyses for a resume"""
        return self.session.query(Analysis).filter_by(resume_id=resume_id).all()
    
    # ============ SKILL GAP OPERATIONS ============
    
    def create_skill_gap(self, analysis_id: int, skill_name: str,
                        skill_type: str, priority: str,
                        recommended_courses: List[Dict],
                        estimated_time: str) -> SkillGap:
        """Save skill gap"""
        gap = SkillGap(
            analysis_id=analysis_id,
            skill_name=skill_name,
            skill_type=skill_type,
            priority=priority,
            recommended_courses=recommended_courses,
            estimated_learning_time=estimated_time
        )
        self.session.add(gap)
        self.session.commit()
        return gap
    
    def get_analysis_gaps(self, analysis_id: int) -> List[SkillGap]:
        """Get all gaps for an analysis"""
        return self.session.query(SkillGap).filter_by(analysis_id=analysis_id).all()
    
    # ============ COMPLEX QUERIES ============
    
    def get_complete_analysis(self, analysis_id: int) -> Dict:
        """Get full analysis with all related data"""
        analysis = self.get_analysis(analysis_id)
        if not analysis:
            return None
        
        resume = self.get_resume(analysis.resume_id)
        job = self.get_job_description(analysis.job_description_id)
        gaps = self.get_analysis_gaps(analysis_id)
        
        return {
            "analysis": {
                "id": analysis.id,
                "match_score": analysis.match_score,
                "matched_skills": analysis.matched_skills,
                "missing_skills": analysis.missing_skills,
                "created_at": analysis.created_at
            },
            "resume": {
                "file_name": resume.file_name,
                "skills": resume.extracted_skills
            },
            "job": {
                "title": job.title,
                "company": job.company,
                "required_skills": job.extracted_skills
            },
            "skill_gaps": [
                {
                    "skill": gap.skill_name,
                    "priority": gap.priority,
                    "courses": gap.recommended_courses,
                    "learning_time": gap.estimated_learning_time
                }
                for gap in gaps
            ]
        }

# Test CRUD operations
if __name__ == "__main__":
    from .models import Database
    
    # Initialize
    db = Database()
    session = db.get_session()
    ops = DatabaseOperations(session)
    
    try:
        # Create user
        user = ops.get_or_create_user("john@example.com", "John Doe")
        print(f"User: {user}")
        
        # Create resume
        resume = ops.create_resume(
            user_id=user.id,
            file_name="johns_resume.pdf",
            raw_text="Experienced Python developer...",
            extracted_skills=["Python", "Django", "SQL"]
        )
        print(f"Resume: {resume}")
        
        # Create job
        job = ops.create_job_description(
            title="Senior Python Developer",
            company="TechCorp",
            description_text="Looking for experienced Python dev...",
            extracted_skills=["Python", "Django", "PostgreSQL", "Docker"]
        )
        print(f"Job: {job}")
        
        # Create analysis
        analysis = ops.create_analysis(
            resume_id=resume.id,
            job_description_id=job.id,
            match_score=66.7,
            matched_skills=["Python", "Django"],
            missing_skills=["PostgreSQL", "Docker"]
        )
        print(f"Analysis: {analysis}")
        
        # Get complete analysis
        complete = ops.get_complete_analysis(analysis.id)
        print("\n=== Complete Analysis ===")
        print(f"Match Score: {complete['analysis']['match_score']}%")
        print(f"Matched: {complete['analysis']['matched_skills']}")
        print(f"Missing: {complete['analysis']['missing_skills']}")
        
    except Exception as e:
        print(f"Error: {e}")
        session.rollback()
    finally:
        session.close()