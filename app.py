from flask import Flask, render_template, request
import os
import pdfplumber
from docx import Document
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

SKILLS = [
    "python", "sql", "excel", "power bi", "tableau", "java", "c++", "html", "css",
    "javascript", "flask", "django", "react", "node.js", "crm", "sales", "communication",
    "teamwork", "problem solving", "project management", "data analysis", "machine learning",
    "ai", "english", "microsoft office", "word", "outlook"
]


def extract_text_from_pdf(file_path):
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception:
        pass
    return text


def extract_text_from_docx(file_path):
    text = ""
    try:
        doc = Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception:
        pass
    return text


def extract_text(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    if ext == ".docx":
        return extract_text_from_docx(file_path)
    return ""


def detect_skills(text):
    text_lower = text.lower()
    found_skills = []

    for skill in SKILLS:
        if skill.lower() in text_lower:
            found_skills.append(skill)

    return sorted(list(set(found_skills)))


def calculate_ats_score(cv_text, found_skills):
    score = 0
    cv_text_lower = cv_text.lower()

    score += min(len(found_skills) * 5, 40)

    sections = ["experience", "education", "skills", "summary", "profile"]
    found_sections = sum(1 for section in sections if section in cv_text_lower)
    score += found_sections * 10

    word_count = len(cv_text.split())
    if 200 <= word_count <= 900:
        score += 20
    elif 100 <= word_count < 200:
        score += 10

    return min(score, 100)


def calculate_job_match(cv_text, job_text):
    if not cv_text.strip() or not job_text.strip():
        return 0

    texts = [cv_text, job_text]
    vectorizer = CountVectorizer().fit_transform(texts)
    similarity = cosine_similarity(vectorizer)[0][1]
    return round(similarity * 100, 2)


def generate_suggestions(found_skills, ats_score, match_score):
    suggestions = []

    if len(found_skills) < 5:
        suggestions.append("CV’ne daha fazla teknik ve profesyonel beceri ekleyebilirsin.")

    if ats_score < 60:
        suggestions.append("CV formatın ATS için daha uygun hale getirilebilir. 'Skills', 'Experience' ve 'Education' başlıklarını net kullan.")

    if match_score < 50:
        suggestions.append("İş ilanındaki anahtar kelimeleri CV’ne daha doğal şekilde eklemelisin.")

    if not suggestions:
        suggestions.append("CV genel olarak iyi görünüyor. Küçük iyileştirmelerle daha da güçlü olabilir.")

    return suggestions


@app.route("/", methods=["GET", "POST"])
def index():
    result = None

    if request.method == "POST":
        uploaded_file = request.files.get("cv_file")
        job_description = request.form.get("job_description", "").strip()

        if uploaded_file and uploaded_file.filename:
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], uploaded_file.filename)
            uploaded_file.save(file_path)

            cv_text = extract_text(file_path)

            found_skills = detect_skills(cv_text)
            ats_score = calculate_ats_score(cv_text, found_skills)
            match_score = calculate_job_match(cv_text, job_description) if job_description else 0
            suggestions = generate_suggestions(found_skills, ats_score, match_score)

            result = {
                "skills": found_skills,
                "ats_score": ats_score,
                "match_score": match_score,
                "suggestions": suggestions,
                "cv_preview": cv_text[:1500]
            }

    return render_template("index.html", result=result)


if __name__ == "__main__":
    os.makedirs("uploads", exist_ok=True)
    app.run(debug=True)
