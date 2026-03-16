import os
import pandas as pd

DATA_DIR = os.path.dirname(__file__)
SKILLS_CSV_PATH = os.path.join(DATA_DIR, "skills_dataset.csv")

df = pd.read_csv(SKILLS_CSV_PATH)

def get_required_skills(job_role):
    return df[df["job_role"] == job_role]["skill"].tolist()

def find_skill_gap(user_skills, job_role):
    required = get_required_skills(job_role)
    return list(set(required) - set(user_skills))

def skill_match_score(user_skills, job_role):
    required = get_required_skills(job_role)
    matched = len(set(user_skills) & set(required))
    return (matched / len(required)) * 100

user_skills = ["Python","SQL"]
target_job = "Data Scientist"

missing = find_skill_gap(user_skills,target_job)

print("Target Job:",target_job)
print("User Skills:",user_skills)
print("Missing Skills:",missing)
print("Skill Match Score:",skill_match_score(user_skills,target_job))