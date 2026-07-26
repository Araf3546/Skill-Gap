# Skill → Course mapping (you'll expand this)
SKILL_COURSE_MAP = {
    "Python": [
        {"name": "Python for Everybody", "platform": "Coursera", "hours": 40},
        {"name": "Complete Python Bootcamp", "platform": "Udemy", "hours": 22}
    ],
    "Machine Learning": [
        {"name": "ML Specialization", "platform": "Coursera", "hours": 80},
        {"name": "ML A-Z", "platform": "Udemy", "hours": 44}
    ],
    "TensorFlow": [
        {"name": "TensorFlow Developer", "platform": "Coursera", "hours": 60},
        {"name": "Complete TensorFlow", "platform": "Udemy", "hours": 20}
    ],
    "AWS": [
        {"name": "AWS Certified Solutions Architect", "platform": "AWS", "hours": 40},
        {"name": "AWS Essentials", "platform": "Udemy", "hours": 18}
    ],
    "Docker": [
        {"name": "Docker & Kubernetes", "platform": "Udemy", "hours": 21},
    ]
}

class CourseRecommender:
    def __init__(self):
        self.course_map = SKILL_COURSE_MAP
    
    def recommend_for_skill(self, skill: str) -> list:
        """Get courses for a skill"""
        return self.course_map.get(skill, [
            {"name": f"Search '{skill}' on Coursera", "platform": "Coursera"}
        ])
    
    def generate_learning_path(self, gaps: list, max_courses: int = 2) -> dict:
        """
        Create personalized learning path
        - Recommend top courses for each gap
        - Estimate total time
        """
        learning_path = []
        total_hours = 0
        
        for gap in gaps[:5]:  # Top 5 gaps only
            skill = gap['skill']
            courses = self.recommend_for_skill(skill)[:max_courses]
            
            skill_entry = {
                "skill": skill,
                "priority": gap['priority'],
                "courses": courses,
                "estimated_hours": sum(c.get('hours', 20) for c in courses)
            }
            
            learning_path.append(skill_entry)
            total_hours += skill_entry['estimated_hours']
        
        return {
            "learning_path": learning_path,
            "estimated_total_hours": total_hours,
            "estimated_months": round(total_hours / 60, 1)  # ~60hrs/month
        }

# Test
if __name__ == "__main__":
    gaps = [
        {"skill": "TensorFlow", "priority": "CRITICAL"},
        {"skill": "AWS", "priority": "IMPORTANT"},
        {"skill": "Docker", "priority": "IMPORTANT"}
    ]
    
    recommender = CourseRecommender()
    path = recommender.generate_learning_path(gaps)
    
    print(f"Learning path: {len(path['learning_path'])} skills")
    print(f"Total time: {path['estimated_months']} months")