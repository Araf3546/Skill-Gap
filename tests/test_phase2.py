from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.preprocessing.resume_processor import ResumeProcessor
from src.preprocessing.job_processor import JobProcessor
from src.matching.skill_matcher import SkillMatcher
from src.analysis.gap_analyzer import GapAnalyzer
from src.recommendations.course_recommender import CourseRecommender

def test_complete_pipeline():
    """Test Days 4-8 pipeline"""
    
    print("\n" + "="*60)
    print("PHASE 2 INTEGRATION TEST")
    print("="*60)
    
    # Day 4: Process resume
    print("\n[1/5] Processing resume...")
    resume_proc = ResumeProcessor()
    resume_result = resume_proc.process_resume("data/raw/sample_resume_1.txt")
    print(f"[OK] Extracted {len(resume_result['skills'])} skills from resume")
    
    # Day 5: Process job
    print("\n[2/5] Processing job description...")
    job_proc = JobProcessor()
    with open("data/raw/job_ml_engineer.txt") as f:
        job_result = job_proc.process_job_description(f.read())
    print(f"[OK] Extracted {len(job_result['skills'])} skills from job")
    
    # Day 6: Match skills
    print("\n[3/5] Matching skills...")
    matcher = SkillMatcher()
    matching = matcher.match_skills(resume_result['skills'], job_result['skills'])
    print(f"[OK] Match rate: {matching['match_percentage']:.1f}%")
    
    # Day 7: Analyze gaps
    print("\n[4/5] Analyzing gaps...")
    analyzer = GapAnalyzer()
    gaps = analyzer.analyze_gaps(matching, {skill: 1 for skill in job_result['skills']})
    report = analyzer.generate_report(matching, gaps)
    print(f"[OK] Found {len(gaps)} skill gaps")
    
    # Day 8: Recommend courses
    print("\n[5/5] Generating learning path...")
    recommender = CourseRecommender()
    path = recommender.generate_learning_path(gaps)
    print(f"[OK] Created path: {path['estimated_months']} months of learning")
    
    print("\n" + "="*60)
    print("[OK] PHASE 2 COMPLETE")
    print("="*60)
    print(f"\nReport Summary:")
    print(f"  Match: {report['summary']['overall_match']:.1f}%")
    print(f"  Matched: {report['summary']['skills_matched']}/{report['summary']['total_skills_required']}")
    print(f"  Priority skills: {path['learning_path'][0]['skill']}")

if __name__ == "__main__":
    test_complete_pipeline()