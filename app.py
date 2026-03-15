from flask import Flask, render_template, request, session, redirect, url_for
import sqlite3

app = Flask(__name__)
app.secret_key = "skillgap_secret"

# Predefined job roles and required skills
JOB_ROLES = {
    "data scientist": [
        "python", "statistics", "machine learning",
        "sql", "data visualization", "pandas", "numpy"
    ],
    "full stack developer": [
        "html", "css", "javascript",
        "python", "flask", "database", "sql"
    ],
    "machine learning engineer": [
        "python", "machine learning", "deep learning",
        "tensorflow", "pandas", "numpy"
    ]
}

# Function to connect database
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def normalize_skills(skills):
    """Simple NLP preprocessing - normalize user input skills"""
    return [skill.strip().lower() for skill in skills.split(',')]

def find_skill_gap(user_skills, role):
    """AI Brain - detect missing skills for target role"""
    required_skills = JOB_ROLES.get(role.lower(), [])
    missing_skills = []
    
    for skill in required_skills:
        if skill not in user_skills:
            missing_skills.append(skill)
    
    return missing_skills

def generate_roadmap(missing_skills, role):
    """Learning Roadmap Generator - role-based personalized recommendations"""
    roadmap = []
    for skill in missing_skills:
        roadmap.append(
            f"Learn {skill} and build a small project related to {role}"
        )
    return roadmap

# Home Page
@app.route('/', methods=['GET', 'POST'])
def index():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        name = request.form['name']
        role = request.form['role']
        skills_input = request.form['skills']
        
        user_skills = normalize_skills(skills_input)
        missing_skills = find_skill_gap(user_skills, role)
        roadmap = generate_roadmap(missing_skills, role)
        
        required_skills = JOB_ROLES.get(role.lower(), [])
        matched_skills = len(required_skills) - len(missing_skills)
        
        return render_template(
            'dashboard.html',
            name=name,
            role=role,
            user_skills=user_skills,
            missing_skills=missing_skills,
            roadmap=roadmap,
            required_count=len(required_skills),
            matched_count=matched_skills,
            missing_count=len(missing_skills)
        )
    
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        try:
            conn.execute(
                'INSERT INTO auth_users (name, email, password) VALUES (?, ?, ?)',
                (name, email, password)
            )
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            conn.close()
            return "Email already exists"

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM auth_users WHERE email=? AND password=?',
            (email, password)
        ).fetchone()
        conn.close()

        if user:
            session['user'] = user['name']
            return redirect(url_for('index'))
        else:
            return "Invalid credentials"

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
