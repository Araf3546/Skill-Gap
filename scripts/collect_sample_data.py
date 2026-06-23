import os
import requests
from pathlib import Path

# Create directories
DATA_DIR = Path("data/raw")
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Sample resume texts (you'll add more)
SAMPLE_RESUMES = [
    {
        "name": "sample_resume_1.txt",
        "content": """
        JOHN DOE
        Senior Software Engineer
        john.doe@email.com | LinkedIn: linkedin.com/in/johndoe
        
        SUMMARY
        Experienced software engineer with 7+ years in full-stack development.
        Passionate about building scalable web applications and leading technical teams.
        
        SKILLS
        Languages: Python, JavaScript, Java, TypeScript
        Frameworks: Django, React, Node.js, Spring Boot
        Databases: PostgreSQL, MongoDB, Redis
        Tools: Docker, Kubernetes, Git, Jenkins, AWS
        Methodologies: Agile, Scrum, TDD
        
        EXPERIENCE
        Senior Software Engineer | TechCorp Inc. | 2020 - Present
        - Led development of microservices architecture serving 1M+ users
        - Implemented CI/CD pipeline reducing deployment time by 60%
        - Mentored 5 junior developers
        
        Software Engineer | StartupXYZ | 2017 - 2020
        - Built RESTful APIs using Python and Django
        - Developed responsive frontend using React and TypeScript
        - Optimized database queries improving performance by 40%
        
        EDUCATION
        Bachelor of Science in Computer Science
        University of Technology | 2017
        """
    },
    {
        "name": "sample_resume_2.txt",
        "content": """
        SARAH JOHNSON
        Data Scientist
        sarah.j@email.com | GitHub: github.com/sarahj
        
        PROFESSIONAL SUMMARY
        Data scientist with 5 years of experience in machine learning and analytics.
        Skilled in building predictive models and deriving insights from complex datasets.
        
        TECHNICAL SKILLS
        Programming: Python, R, SQL
        ML/AI: TensorFlow, PyTorch, scikit-learn, Keras
        Data: Pandas, NumPy, Matplotlib, Seaborn
        Big Data: Spark, Hadoop
        Cloud: AWS (SageMaker, S3, EC2), GCP
        
        WORK EXPERIENCE
        Data Scientist | DataCorp | 2021 - Present
        - Developed ML models for customer churn prediction (92% accuracy)
        - Built recommendation system using collaborative filtering
        - Automated data pipelines processing 10TB+ data daily
        
        Junior Data Scientist | Analytics Co | 2019 - 2021
        - Created dashboards using Tableau and Power BI
        - Performed A/B testing and statistical analysis
        - Cleaned and processed large datasets using Python
        
        EDUCATION
        Master of Science in Data Science | MIT | 2019
        Bachelor of Science in Statistics | UCLA | 2017
        
        CERTIFICATIONS
        - AWS Certified Machine Learning - Specialty
        - TensorFlow Developer Certificate
        """
    }
]

# Sample job descriptions
SAMPLE_JOBS = [
    {
        "name": "job_ml_engineer.txt",
        "content": """
        MACHINE LEARNING ENGINEER
        TechGiant Inc. | San Francisco, CA | Full-time
        
        ABOUT THE ROLE
        We're looking for a Machine Learning Engineer to join our AI team.
        You'll work on cutting-edge ML projects impacting millions of users.
        
        REQUIREMENTS
        - 3+ years of experience in machine learning
        - Strong proficiency in Python and ML frameworks (TensorFlow, PyTorch)
        - Experience with deep learning and neural networks
        - Knowledge of MLOps and model deployment
        - Familiarity with cloud platforms (AWS, GCP, or Azure)
        - Strong understanding of data structures and algorithms
        
        PREFERRED QUALIFICATIONS
        - Experience with Kubernetes and Docker
        - Knowledge of distributed computing (Spark, Hadoop)
        - Publications in top ML conferences
        - Master's degree in CS, ML, or related field
        
        RESPONSIBILITIES
        - Design and implement ML models for production
        - Optimize model performance and scalability
        - Collaborate with cross-functional teams
        - Mentor junior engineers
        
        TECH STACK
        Python, TensorFlow, PyTorch, Kubernetes, AWS, PostgreSQL, Redis
        """
    },
    {
        "name": "job_fullstack_dev.txt",
        "content": """
        SENIOR FULL-STACK DEVELOPER
        InnovateLabs | Remote | Full-time
        
        WE'RE LOOKING FOR
        An experienced full-stack developer to build our next-generation platform.
        You'll architect solutions and lead technical implementation.
        
        MUST-HAVE SKILLS
        - 5+ years professional software development
        - Expert in JavaScript/TypeScript
        - Strong backend experience (Node.js, Python, or Java)
        - Frontend mastery (React, Vue, or Angular)
        - Database design (SQL and NoSQL)
        - RESTful API development
        - Version control (Git)
        
        BONUS POINTS
        - Experience with GraphQL
        - Knowledge of microservices architecture
        - Containerization (Docker, Kubernetes)
        - Cloud platforms (AWS, Azure, GCP)
        - CI/CD pipeline setup
        - Agile/Scrum experience
        
        WHAT YOU'LL DO
        - Build scalable web applications
        - Design database schemas
        - Write clean, testable code
        - Review code and mentor team members
        - Participate in architecture decisions
        
        OUR TECH STACK
        TypeScript, React, Node.js, PostgreSQL, MongoDB, Docker, AWS, GitHub Actions
        """
    }
]

def save_samples():
    """Save sample data to files"""
    # Save resumes
    for resume in SAMPLE_RESUMES:
        file_path = DATA_DIR / resume["name"]
        with open(file_path, 'w') as f:
            f.write(resume["content"])
        print(f"Saved: {file_path}")
    
    # Save job descriptions
    for job in SAMPLE_JOBS:
        file_path = DATA_DIR / job["name"]
        with open(file_path, 'w') as f:
            f.write(job["content"])
        print(f"Saved: {file_path}")
    
    print(f"\n✅ Saved {len(SAMPLE_RESUMES)} resumes and {len(SAMPLE_JOBS)} job descriptions")

if __name__ == "__main__":
    save_samples()
    print("\n" + "="*50)
    print("NEXT STEPS:")
    print("1. Add more sample resumes to data/raw/")
    print("2. Add more job descriptions")
    print("3. Test skill extraction on these samples")
    print("="*50)