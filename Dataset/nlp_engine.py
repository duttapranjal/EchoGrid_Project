import os
import pandas as pd
import re
import spacy
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

from Dataset.skill_gap import find_skill_gap
from Dataset.predict_job import model, mlb
from Dataset.ats_score import calculate_ats_score
from Dataset.learning_path import generate_learning_path

nltk.download('punkt')
nltk.download('stopwords')
nlp = spacy.load('en_core_web_sm')

# Load dataset
DATA_DIR = os.path.dirname(__file__)
SKILLS_CSV_PATH = os.path.join(DATA_DIR, "skills_dataset.csv")
df = pd.read_csv(SKILLS_CSV_PATH)

# Get all unique skills from dataset
ALL_SKILLS = [s.lower() for s in df["skill"].unique()]

stop_words = set(stopwords.words("english"))

def preprocess_text(text):

    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9 ]', ' ', text)
    tokens = word_tokenize(text)
    filtered_tokens = [w for w in tokens if w not in stop_words]
    
    return " ".join(filtered_tokens)

def extract_skills(resume_text):

    clean_text = preprocess_text(resume_text)
    doc = nlp(clean_text)
    
    found_skills = []
    
    for token in doc:
        if token.text in ALL_SKILLS:
            found_skills.append(token.text)
            
            
    for skill in ALL_SKILLS:
        if skill in clean_text:
            found_skills.append(skill)

    return list(set(found_skills))


# Resume Analyzer Pipeline
def analyze_resume(resume_text, job_role):

    skills = extract_skills(resume_text)

    X = mlb.transform([skills])
    predicted_role = model.predict(X)[0]

    missing = find_skill_gap(skills, job_role)

    ats = calculate_ats_score(skills, job_role)

    roadmap = generate_learning_path(missing)
    
    return {
        "extracted_skills": skills,
        "predicted_job": predicted_role,
        "missing_skills": missing,
        "ats_score": ats,
        "learning_path": roadmap
    }
    
# Test
if __name__ == "__main__":

    resume = """
    I have experience in Python, SQL, Machine Learning and Pandas.
    """

    job_role = "Data Scientist"

    result = analyze_resume(resume, job_role)

    print("\nResume Analysis Result")
    print("----------------------")
    print("Extracted Skills:", result["extracted_skills"])
    print("Predicted Job Role:", result["predicted_job"])
    print("Missing Skills:", result["missing_skills"])
    print("ATS Score:", result["ats_score"])
    print("Learning Path:", result["learning_path"])
