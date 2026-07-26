from enum import Enum

class Priority(Enum):
    CRITICAL = 1    # Frequently mentioned, required
    IMPORTANT = 2   # Mentioned multiple times
    NICE_TO_HAVE = 3

class GapAnalyzer:
    def analyze_gaps(self, matching_result: dict, 
                    job_skills_count: dict) -> list:
        """
        Prioritize missing skills based on:
        - Frequency in job posting
        - Skill category (hard vs soft)
        """
        gaps = []
        
        for missing_skill in matching_result['missing']:
            # Determine priority
            if job_skills_count.get(missing_skill, 0) >= 3:
                priority = Priority.CRITICAL.name
                weight = 1.0
            elif job_skills_count.get(missing_skill, 0) >= 2:
                priority = Priority.IMPORTANT.name
                weight = 0.7
            else:
                priority = Priority.NICE_TO_HAVE.name
                weight = 0.4
            
            gaps.append({
                "skill": missing_skill,
                "priority": priority,
                "weight": weight,
                "frequency": job_skills_count.get(missing_skill, 1)
            })
        
        # Sort by priority
        gaps.sort(key=lambda x: x['weight'], reverse=True)
        
        return gaps
    
    def generate_report(self, matching_result: dict, gaps: list) -> dict:
        """Generate analysis report"""
        total_skills = matching_result['total_required']
        matched = matching_result['matched_count']
        
        return {
            "summary": {
                "overall_match": matching_result['match_percentage'],
                "total_skills_required": total_skills,
                "skills_matched": matched,
                "skills_missing": len(gaps)
            },
            "matched_skills": [m['job_skill'] for m in matching_result['matched']],
            "skill_gaps": gaps,
            "learning_priority_order": [g['skill'] for g in gaps]
        }

# Test
if __name__ == "__main__":
    matching = {
        "matched": [{"job_skill": "Python"}],
        "missing": ["TensorFlow", "AWS", "Docker"],
        "match_percentage": 25.0,
        "total_required": 4,
        "matched_count": 1
    }
    
    job_skills_freq = {"TensorFlow": 5, "AWS": 3, "Docker": 1}
    
    analyzer = GapAnalyzer()
    gaps = analyzer.analyze_gaps(matching, job_skills_freq)
    report = analyzer.generate_report(matching, gaps)
    
    print("Priority order:", report['learning_priority_order'])