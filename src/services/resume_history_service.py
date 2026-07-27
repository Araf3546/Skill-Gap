from src.database.models import db, ResumeVersion
from sqlalchemy import func

class ResumeHistoryService:
    def save_version(self, user_id: int, file_name: str, skills: list) -> ResumeVersion:
        latest = db.session.query(func.max(ResumeVersion.version_number)) \
            .filter_by(user_id=user_id).scalar() or 0

        version = ResumeVersion(
            user_id=user_id,
            version_number=latest + 1,
            file_name=file_name,
            extracted_skills=skills
        )
        db.session.add(version)
        db.session.commit()
        return version

    def get_history(self, user_id: int) -> list:
        versions = ResumeVersion.query.filter_by(user_id=user_id) \
            .order_by(ResumeVersion.version_number.desc()).all()
        return [{
            "version": v.version_number,
            "file_name": v.file_name,
            "skill_count": len(v.extracted_skills),
            "created_at": v.created_at.isoformat()
        } for v in versions]

    def compare_versions(self, user_id: int, v1: int, v2: int) -> dict:
        version1 = ResumeVersion.query.filter_by(user_id=user_id, version_number=v1).first()
        version2 = ResumeVersion.query.filter_by(user_id=user_id, version_number=v2).first()

        if not version1 or not version2:
            raise ValueError("One or both versions not found")

        skills1, skills2 = set(version1.extracted_skills), set(version2.extracted_skills)
        return {
            "gained_skills": list(skills2 - skills1),
            "lost_skills": list(skills1 - skills2),
            "common_skills": list(skills1 & skills2)
        }