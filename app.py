from flask import Flask, render_template, request, session, redirect, url_for, jsonify
import sqlite3

app = Flask(__name__)
app.secret_key = "skillgap_secret"

# ── Job Roles & Required Skills ──────────────────────────────────────────────
JOB_ROLES = {
    "data scientist": [
        "python", "statistics", "machine learning",
        "sql", "data visualization", "pandas", "numpy", "r", "deep learning", "feature engineering"
    ],
    "full stack developer": [
        "html", "css", "javascript", "python", "flask",
        "database", "sql", "react", "nodejs", "rest api"
    ],
    "machine learning engineer": [
        "python", "machine learning", "deep learning",
        "tensorflow", "pandas", "numpy", "mlops", "docker", "kubernetes", "pytorch"
    ],
    "frontend developer": [
        "html", "css", "javascript", "react", "typescript",
        "responsive design", "figma", "webpack", "accessibility", "performance optimization"
    ],
    "backend developer": [
        "python", "nodejs", "sql", "nosql", "rest api",
        "docker", "microservices", "redis", "authentication", "system design"
    ],
    "devops engineer": [
        "linux", "docker", "kubernetes", "ci/cd", "aws",
        "terraform", "ansible", "monitoring", "networking", "scripting"
    ],
    "product manager": [
        "roadmapping", "user research", "agile", "jira", "data analysis",
        "stakeholder management", "wireframing", "a/b testing", "communication", "prioritization"
    ],
    "ux designer": [
        "figma", "user research", "wireframing", "prototyping", "usability testing",
        "design thinking", "information architecture", "adobe xd", "accessibility", "typography"
    ],
    "cloud architect": [
        "aws", "azure", "gcp", "terraform", "kubernetes",
        "networking", "security", "cost optimization", "microservices", "serverless"
    ],
    "mobile developer": [
        "react native", "flutter", "swift", "kotlin", "rest api",
        "firebase", "mobile ui", "app store deployment", "push notifications", "offline storage"
    ],
}

# ── Trending Skills per Role ──────────────────────────────────────────────────
TRENDING_SKILLS = {
    "data scientist":           ["LLMs", "RAG", "Vector Databases", "LangChain", "MLflow", "dbt", "Snowflake", "Spark"],
    "full stack developer":     ["Next.js", "TypeScript", "GraphQL", "Docker", "Tailwind CSS", "tRPC", "Prisma", "Bun"],
    "machine learning engineer":["LLMOps", "LangChain", "Hugging Face", "LoRA Fine-tuning", "ONNX", "Ray Serve", "Triton"],
    "frontend developer":       ["Next.js", "TypeScript", "Tailwind CSS", "Framer Motion", "Server Components", "WebAssembly"],
    "backend developer":        ["Go", "Rust", "gRPC", "Message Queues", "Event Sourcing", "CQRS", "Rate Limiting"],
    "devops engineer":          ["Platform Engineering", "GitOps", "eBPF", "OpenTelemetry", "ArgoCD", "Cilium", "Backstage"],
    "product manager":          ["AI Product Management", "Product-Led Growth", "OKRs", "Jobs-to-be-done", "Growth Metrics"],
    "ux designer":              ["AI-Assisted Design", "Motion Design", "3D/Spatial UI", "Voice UI", "Design Systems"],
    "cloud architect":          ["FinOps", "Multi-Cloud Strategy", "Zero Trust Security", "Edge Computing", "Service Mesh"],
    "mobile developer":         ["Compose Multiplatform", "SwiftUI", "On-Device ML", "AR/VR", "WebRTC", "Bluetooth LE"],
}

# ── Learning Resource Hints ───────────────────────────────────────────────────
RESOURCES = {
    "python":           "freeCodeCamp, Python.org, or Automate the Boring Stuff",
    "javascript":       "javascript.info or The Odin Project",
    "typescript":       "TypeScript official docs or Matt Pocock's Total TypeScript",
    "react":            "React official docs or Scrimba React course",
    "machine learning": "fast.ai or Andrew Ng's ML Specialization (Coursera)",
    "deep learning":    "fast.ai Part 2 or deeplearning.ai Specialization",
    "sql":              "SQLZoo, Mode Analytics, or LeetCode SQL",
    "docker":           "Docker official docs or TechWorld with Nana (YouTube)",
    "kubernetes":       "Kubernetes.io docs or KodeKloud",
    "aws":              "AWS free tier + AWS Skill Builder",
    "figma":            "Figma Academy or DesignCourse (YouTube)",
    "tensorflow":       "TensorFlow official tutorials or Keras.io",
    "pytorch":          "PyTorch.org tutorials or fast.ai",
    "nodejs":           "Node.js official docs or The Odin Project",
    "linux":            "Linux Journey (linuxjourney.com) or TLCL book",
    "terraform":        "HashiCorp Learn (developer.hashicorp.com)",
    "flutter":          "Flutter official docs or Angela Yu's Flutter course (Udemy)",
}


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


def normalize_skills(skills):
    return [s.strip().lower() for s in skills.split(',') if s.strip()]


def find_skill_gap(user_skills, role):
    required = JOB_ROLES.get(role.lower(), [])
    return [s for s in required if s not in user_skills]


def generate_roadmap(missing_skills, role):
    roadmap = []
    for skill in missing_skills:
        resource = RESOURCES.get(skill, f"search '{skill}' on Coursera, Udemy, or YouTube")
        roadmap.append({
            "skill": skill.title(),
            "action": f"Learn {skill.title()} — {resource}",
            "project": f"Build a small project showcasing {skill} for your {role} portfolio"
        })
    return roadmap


# ── Routes ────────────────────────────────────────────────────────────────────
@app.route('/', methods=['GET', 'POST'])
def index():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        name        = request.form.get('name', 'User')
        role        = request.form.get('role', '').lower()
        skills_input = request.form.get('skills', '')

        user_skills    = normalize_skills(skills_input)
        missing_skills = find_skill_gap(user_skills, role)
        roadmap        = generate_roadmap(missing_skills, role)

        required_skills = JOB_ROLES.get(role, [])
        matched_count   = len(required_skills) - len(missing_skills)
        match_pct       = round((matched_count / len(required_skills)) * 100) if required_skills else 0

        return render_template(
            'dashboard.html',
            name=name,
            role=role.title(),
            user_skills=user_skills,
            missing_skills=missing_skills,
            roadmap=roadmap,
            required_count=len(required_skills),
            matched_count=matched_count,
            missing_count=len(missing_skills),
            match_pct=match_pct,
        )

    return render_template('index.html')


@app.route('/api/trending', methods=['POST'])
def get_trending():
    data  = request.get_json()
    role  = data.get('role', '').lower()
    skills = TRENDING_SKILLS.get(role, ["Python", "AI/ML", "TypeScript", "Docker", "Cloud", "LLMs"])
    return jsonify({"trending_skills": skills})


@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        name     = request.form['name']
        email    = request.form['email']
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
            error = "An account with this email already exists."
    return render_template('register.html', error=error)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email    = request.form['email']
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
            error = "Invalid email or password. Please try again."
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))


if __name__ == '__main__':
    print("\n🚀 Skill Gap Analyzer is running!")
    print("🌐 Open in browser: \033[94mhttp://127.0.0.1:5000\033[0m\n")
    app.run(debug=True)
