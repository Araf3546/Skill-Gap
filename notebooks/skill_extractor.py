# Cell 1: Setup
from skillNER.general_params import SKILL_DB
from skillNER.skill_extractor_class import SkillExtractor
import spacy
# Load spaCy model
nlp = spacy.load("en_core_web_lg")
# Initialize skill extractor
skill_extractor = SkillExtractor(nlp, SKILL_DB, PhraseMatcher)

resume_text = """
Senior Software Engineer with 8 years of experience in full-stack development.
Expertise in Python, JavaScript, React, Node.js, and AWS.
Strong background in Machine Learning and Deep Learning using TensorFlow and PyTorch.
Proficient in SQL, MongoDB, and PostgreSQL databases.
Experience with Docker, Kubernetes, and CI/CD pipelines.
"""
annotations = skill_extractor.annotate(resume_text)
# Cell 3: Display results
print("Full-match Skills (exact matches):")
for skill in annotations['results']['full_matches']:
    
    print(f" - {skill['doc_node_value']} (type: {skill['type']})")
    
print("\nNgram-match Skills (partial matches):")
for skill in annotations['results']['ngram_scored']:
    print(f" - {skill['doc_node_value']} (score: {skill['score']})")
    
# Cell 4: Test on job description
job_text = """
We are seeking a Machine Learning Engineer with strong Python skills.
Requirements:
- 5+ years experience in ML/AI
- Proficiency in TensorFlow, PyTorch, or scikit-learn
- Experience with cloud platforms (AWS, GCP, or Azure)
- Knowledge of Docker and Kubernetes
- Strong understanding of deep learning architectures
"""
job_annotations = skill_extractor.annotate(job_text)
print("\nJob Description Skills:")
for skill in job_annotations['results']['full_matches']:
    print(f" - {skill['doc_node_value']}")
print('done')
