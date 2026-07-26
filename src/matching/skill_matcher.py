import re
from typing import Any

try:
    import numpy as np
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
except Exception:  # pragma: no cover - optional dependency fallback
    np = None
    SentenceTransformer = None
    cosine_similarity = None

class SkillMatcher:
    def __init__(self):
        self.model = None
        self.fallback_mode = SentenceTransformer is None or cosine_similarity is None
        if not self.fallback_mode:
            try:
                # Pre-trained model: fast and accurate
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
            except Exception:
                self.model = None
                self.fallback_mode = True
    
    def get_skill_embedding(self, skill: str) -> Any:
        """Convert skill to vector"""
        if self.fallback_mode or self.model is None:
            return skill
        return self.model.encode(skill, convert_to_tensor=False)

    def _normalize_skill(self, skill: str) -> str:
        return re.sub(r"[^a-z0-9\+\#]+", " ", skill.lower()).strip()

    def _fallback_similarity(self, skill1: str, skill2: str) -> float:
        normalized_1 = self._normalize_skill(skill1)
        normalized_2 = self._normalize_skill(skill2)

        if not normalized_1 or not normalized_2:
            return 0.0

        if normalized_1 == normalized_2:
            return 1.0

        tokens_1 = set(normalized_1.split())
        tokens_2 = set(normalized_2.split())
        if not tokens_1 or not tokens_2:
            return 0.0

        return len(tokens_1 & tokens_2) / len(tokens_1 | tokens_2)
    
    def calculate_similarity(self, skill1: str, skill2: str) -> float:
        """Calculate similarity between two skills (0-1)"""
        if self.fallback_mode or self.model is None:
            return self._fallback_similarity(skill1, skill2)

        emb1 = self.get_skill_embedding(skill1)
        emb2 = self.get_skill_embedding(skill2)
        similarity = cosine_similarity([emb1], [emb2])[0][0]
        return float(similarity)
    
    def match_skills(self, resume_skills: list, job_skills: list, 
                     threshold: float = 0.6) -> dict:
        """
        Match resume skills to job requirements
        threshold: minimum similarity to count as match (0-1)
        """
        matched = []
        missing = []
        
        for job_skill in job_skills:
            best_match = None
            best_score = 0
            
            # Find best matching resume skill
            for resume_skill in resume_skills:
                score = self.calculate_similarity(resume_skill, job_skill)
                if score > best_score:
                    best_score = score
                    best_match = resume_skill
            
            # If match above threshold, add to matched
            if best_score >= threshold:
                matched.append({
                    "job_skill": job_skill,
                    "resume_skill": best_match,
                    "similarity": float(best_score)
                })
            else:
                missing.append(job_skill)
        
        match_percentage = (len(matched) / len(job_skills) * 100) if job_skills else 0
        
        return {
            "matched": matched,
            "missing": missing,
            "match_percentage": match_percentage,
            "total_required": len(job_skills),
            "matched_count": len(matched),
            "missing_count": len(missing)
        }

# Test
if __name__ == "__main__":
    resume_skills = ["Python", "Machine Learning", "SQL", "Django"]
    job_skills = ["Python", "Deep Learning", "PostgreSQL", "FastAPI", "AWS"]
    
    matcher = SkillMatcher()
    result = matcher.match_skills(resume_skills, job_skills)
    
    print(f"Match rate: {result['match_percentage']:.1f}%")
    print(f"Matched: {[m['job_skill'] for m in result['matched']]}")
    print(f"Missing: {result['missing']}")