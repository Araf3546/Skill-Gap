import json
import logging
import re
from pathlib import Path
from typing import Dict, List

try:
    import spacy
    from skillNer.general_params import SKILL_DB
    from skillNer.skill_extractor_class import SkillExtractor
    from spacy.matcher import PhraseMatcher
except Exception:  # pragma: no cover - optional dependency fallback
    spacy = None
    SKILL_DB = None
    SkillExtractor = None
    PhraseMatcher = None


COMMON_SKILLS = [
    "Python",
    "JavaScript",
    "TypeScript",
    "Java",
    "Django",
    "React",
    "Node.js",
    "Spring Boot",
    "PostgreSQL",
    "MongoDB",
    "Redis",
    "Docker",
    "Kubernetes",
    "AWS",
    "GCP",
    "Azure",
    "TensorFlow",
    "PyTorch",
    "Machine Learning",
    "Deep Learning",
    "MLOps",
    "Spark",
    "Hadoop",
    "SQL",
    "Git",
    "Jenkins",
    "Agile",
    "Scrum",
    "TDD",
]

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SkillExtractorPipeline:
    """Extract skills from resumes and job descriptions"""
    
    def __init__(self):
        """Initialize the skill extractor"""
        try:
            self.fallback_mode = spacy is None or SkillExtractor is None
            if not self.fallback_mode:
                # Load spaCy model
                logger.info("Loading spaCy model...")
                self.nlp = spacy.load("en_core_web_lg")

                # Initialize skillNER
                logger.info("Initializing skillNER...")
                self.skill_extractor = SkillExtractor(self.nlp, SKILL_DB, PhraseMatcher)

                logger.info("Skill extractor initialized successfully")
        except Exception as e:
            logger.warning(f"Falling back to lightweight skill extraction: {e}")
            self.fallback_mode = True
            self.skill_extractor = None
    
    def extract_skills(self, text: str, threshold: float = 0.5) -> Dict[str, any]:
        """
        Extract skills from text
        
        Args:
            text: Input text (resume or job description)
            threshold: Minimum confidence score for ngram matches
            
        Returns:
            Dictionary containing extracted skills and metadata
        """
        if not text or len(text.strip()) == 0:
            logger.warning("Empty text provided")
            return {"skills": [], "metadata": {}}
        
        try:
            if self.fallback_mode:
                skills = self._extract_skills_fallback(text)
                return {
                    "skills": skills,
                    "metadata": {
                        "total_skills": len(skills),
                        "full_matches": len(skills),
                        "ngram_matches": 0,
                        "text_length": len(text),
                        "fallback": True,
                    },
                }

            # Extract skills using skillNER
            annotations = self.skill_extractor.annotate(text)
            
            # Process full matches (high confidence)
            full_matches = self._process_full_matches(
                annotations['results']['full_matches']
            )
            
            # Process ngram matches (partial/lower confidence)
            ngram_matches = self._process_ngram_matches(
                annotations['results']['ngram_scored'],
                threshold
            )
            
            # Combine and deduplicate
            all_skills = self._deduplicate_skills(full_matches, ngram_matches)
            
            return {
                "skills": all_skills,
                "metadata": {
                    "total_skills": len(all_skills),
                    "full_matches": len(full_matches),
                    "ngram_matches": len(ngram_matches),
                    "text_length": len(text)
                }
            }
            
        except Exception as e:
            logger.error(f"Skill extraction failed: {e}")
            skills = self._extract_skills_fallback(text)
            return {
                "skills": skills,
                "metadata": {"error": str(e), "fallback": True, "text_length": len(text)},
            }

    def _normalize_text(self, text: str) -> str:
        return re.sub(r"[^a-z0-9\+\#]+", " ", text.lower())

    def _extract_skills_fallback(self, text: str) -> List[Dict]:
        normalized_text = self._normalize_text(text)
        extracted = []
        seen = set()

        for skill in COMMON_SKILLS:
            normalized_skill = self._normalize_text(skill).strip()
            if normalized_skill and normalized_skill in normalized_text and skill.lower() not in seen:
                seen.add(skill.lower())
                extracted.append({
                    "skill": skill,
                    "type": "Hard Skill",
                    "confidence": 1.0,
                })

        return extracted
    
    def _process_full_matches(self, matches: List[Dict]) -> List[Dict]:
        """Process full skill matches"""
        skills = []
        for match in matches:
            skills.append({
                "skill": match['doc_node_value'],
                "type": match.get('type', 'Unknown'),
                "confidence": 1.0,  # Full matches are high confidence
            })
        return skills
    
    def _process_ngram_matches(self, matches: List[Dict], threshold: float) -> List[Dict]:
        """Process partial skill matches above threshold"""
        skills = []
        for match in matches:
            score = match.get('score', 0)
            if score >= threshold:
                skills.append({
                    "skill": match['doc_node_value'],
                    "type": match.get('type', 'Unknown'),
                    "confidence": score,
                })
        return skills
    
    def _deduplicate_skills(self, full_matches: List[Dict], ngram_matches: List[Dict]) -> List[Dict]:
        """Remove duplicate skills, prioritizing full matches"""
        seen_skills = set()
        unique_skills = []
        
        # Add full matches first (higher priority)
        for skill in full_matches:
            skill_lower = skill['skill'].lower()
            if skill_lower not in seen_skills:
                seen_skills.add(skill_lower)
                unique_skills.append(skill)
        
        # Add ngram matches if not already present
        for skill in ngram_matches:
            skill_lower = skill['skill'].lower()
            if skill_lower not in seen_skills:
                seen_skills.add(skill_lower)
                unique_skills.append(skill)
        
        return unique_skills
    
    def extract_skills_list(self, text: str) -> List[str]:
        """
        Simple method to get just the list of skill names
        
        Args:
            text: Input text
            
        Returns:
            List of skill names
        """
        result = self.extract_skills(text)
        return [skill['skill'] for skill in result['skills']]
    
    def compare_skills(self, resume_text: str, job_text: str) -> Dict:
        """
        Compare skills from resume and job description
        
        Args:
            resume_text: Resume content
            job_text: Job description content
            
        Returns:
            Dictionary with matched and missing skills
        """
        # Extract skills from both
        resume_skills = set(self.extract_skills_list(resume_text))
        job_skills = set(self.extract_skills_list(job_text))
        
        # Find matches and gaps
        matched = resume_skills.intersection(job_skills)
        missing = job_skills - resume_skills
        extra = resume_skills - job_skills
        
        return {
            "matched_skills": list(matched),
            "missing_skills": list(missing),
            "additional_skills": list(extra),
            "match_percentage": len(matched) / len(job_skills) * 100 if job_skills else 0
        }

# Test the extractor
if __name__ == "__main__":
    # Initialize
    extractor = SkillExtractorPipeline()
    
    # Test resume
    resume = """
    Senior Data Scientist with 6 years of experience.
    Skills: Python, R, Machine Learning, Deep Learning, TensorFlow, PyTorch
    Experience with SQL, MongoDB, and data visualization using Tableau.
    """
    
    # Test job description
    job = """
    Looking for Data Scientist with:
    - Python and R programming
    - Machine Learning expertise
    - Experience with TensorFlow or PyTorch
    - SQL and big data technologies
    - Strong communication skills
    """
    
    # Extract from resume
    print("=== Resume Skills ===")
    resume_result = extractor.extract_skills(resume)
    for skill in resume_result['skills']:
        print(f"  {skill['skill']} (confidence: {skill['confidence']:.2f})")
    
    print("\n=== Job Skills ===")
    job_result = extractor.extract_skills(job)
    for skill in job_result['skills']:
        print(f"  {skill['skill']} (confidence: {skill['confidence']:.2f})")
    
    # Compare
    print("\n=== Comparison ===")
    comparison = extractor.compare_skills(resume, job)
    print(f"Match rate: {comparison['match_percentage']:.1f}%")
