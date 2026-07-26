from src.extraction.skill_extractor import SkillExtractorPipeline
from src.preprocessing.text_cleaner import TextPreprocessor


class JobProcessor:
    def __init__(self):
        self.skill_extractor = SkillExtractorPipeline()
        self.preprocessor = TextPreprocessor()

    def process_job_description(self, text: str) -> dict:
        """
        Complete job description processing:
        Clean text → Extract skills
        """
        cleaned_text = " ".join(self.preprocessor.preprocess(text))
        skills_result = self.skill_extractor.extract_skills(text)
        skills = [skill['skill'] for skill in skills_result['skills']]

        return {
            "raw_text": text,
            "cleaned_text": cleaned_text,
            "skills": skills,
            "skill_count": len(skills),
            "text_length": len(text)
        }


if __name__ == "__main__":
    processor = JobProcessor()
    with open("data/raw/job_ml_engineer.txt", "r") as file:
        result = processor.process_job_description(file.read())
    print(f"Skills extracted: {result['skills'][:5]}...")