import re
from pathlib import Path
from src.extraction.skill_extractor import SkillExtractorPipeline
from src.preprocessing.text_cleaner import TextPreprocessor

class ResumeProcessor:
    def __init__(self):
        self.skill_extractor = SkillExtractorPipeline()
        self.preprocessor = TextPreprocessor()
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF"""
        text = ""
        try:
            import pdfplumber

            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
        except Exception as e:
            raise ValueError(f"PDF extraction failed: {e}")
        return text
    
    def process_resume(self, file_path: str) -> dict:
        """
        Complete resume processing:
        PDF/Text → Clean text → Extract skills
        """
        # Extract text
        if file_path.endswith('.pdf'):
            raw_text = self.extract_text_from_pdf(file_path)
        else:
            with open(file_path, 'r') as f:
                raw_text = f.read()
        
        # Extract skills
        skills_result = self.skill_extractor.extract_skills(raw_text)
        skills = [s['skill'] for s in skills_result['skills']]
        
        return {
            "raw_text": raw_text,
            "skills": skills,
            "skill_count": len(skills),
            "text_length": len(raw_text)
        }

# Test
if __name__ == "__main__":
    processor = ResumeProcessor()
    result = processor.process_resume("data/raw/sample_resume_1.txt")
    print(f"Skills extracted: {result['skills'][:5]}...")