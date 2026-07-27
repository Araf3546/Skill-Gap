from src.database.models import db, SkillFeedback
from sqlalchemy import case, func

class FeedbackService:
    def record_feedback(self, user_id: int, resume_version_id: int,
                        skill_name: str, is_correct: bool) -> SkillFeedback:
        feedback = SkillFeedback(
            user_id=user_id,
            resume_version_id=resume_version_id,
            skill_name=skill_name,
            is_correct=is_correct
        )
        db.session.add(feedback)
        db.session.commit()
        return feedback

    def get_skill_accuracy_report(self) -> list:
        """
        Aggregate across ALL users: which skills does the extractor
        get wrong most often? Use this to build a correction/synonym list.
        """
        results = db.session.query(
            SkillFeedback.skill_name,
            func.count(SkillFeedback.id).label('total'),
            func.sum(case((SkillFeedback.is_correct == False, 1), else_=0)).label('incorrect')
        ).group_by(SkillFeedback.skill_name).all()

        report = []
        for skill, total, incorrect in results:
            accuracy = ((total - incorrect) / total * 100) if total > 0 else 0
            report.append({
                "skill": skill,
                "total_feedback": total,
                "incorrect_count": incorrect,
                "accuracy_pct": round(accuracy, 1)
            })
        return sorted(report, key=lambda x: x['accuracy_pct'])
