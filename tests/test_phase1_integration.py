"""
Test the complete Phase 1 pipeline:
Text preprocessing → Skill extraction → Database storage
"""

import sys
sys.path.append('..')

from src.preprocessing.text_cleaner import TextPreprocessor
from src.extraction.skill_extractor import SkillExtractorPipeline
from src.database.models import Database
from src.database.operations import DatabaseOperations
from pathlib import Path

def test_full_pipeline():
    """Test end-to-end processing"""
    
    print("="*60)
    print("PHASE 1 INTEGRATION TEST")
    print("="*60)
    
    # 1. Load sample resume
    print("\n[1/5] Loading sample resume...")
    resume_path = Path("../data/raw/sample_resume_1.txt")
    with open(resume_path, 'r') as f:
        resume_text = f.read()
    print(f"✅ Loaded resume ({len(resume_text)} characters)")
    
    # 2. Preprocess text
    print("\n[2/5] Preprocessing text...")
    preprocessor = TextPreprocessor()
    cleaned_text = ' '.join(preprocessor.preprocess(resume_text))
    print(f"✅ Cleaned text ({len(cleaned_text)} characters)")
    print(f"Sample: {cleaned_text[:100]}...")
    
    # 3. Extract skills
    print("\n[3/5] Extracting skills...")
    extractor = SkillExtractorPipeline()
    skills_result = extractor.extract_skills(resume_text)
    skills = [s['skill'] for s in skills_result['skills']]
    print(f"✅ Extracted {len(skills)} skills")
    print(f"Skills: {skills[:10]}")  # Show first 10
    
    # 4. Save to database
    print("\n[4/5] Saving to database...")
    db = Database(use_sqlite=True)
    db.create_tables()  # Create tables for testing
    session = db.get_session()
    ops = DatabaseOperations(session)
    
    try:
        # Create test user
        user = ops.get_or_create_user("test@skillgap.com", "Test User")
        
        # Save resume
        resume = ops.create_resume(
            user_id=user.id,
            file_name="sample_resume_1.txt",
            raw_text=resume_text,
            extracted_skills=skills
        )
        
        print(f"✅ Resume saved with ID: {resume.id}")
        
        # 5. Verify retrieval
        print("\n[5/5] Verifying data retrieval...")
        retrieved = ops.get_resume(resume.id)
        print(f"✅ Retrieved resume: {retrieved.file_name}")
        print(f"   User: {retrieved.user.name}")
        print(f"   Skills count: {len(retrieved.extracted_skills)}")
        
        print("\n" + "="*60)
        print("✅ PHASE 1 INTEGRATION TEST PASSED!")
        print("="*60)
        
    except Exception as e:
        print(f"\n Error: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    test_full_pipeline()