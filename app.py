from flask import Flask, render_template, request
import os
from services.ats import (
    detect_skills,
    calculate_ats_score,
    calculate_job_match
)

from services.parser import (
    extract_text_from_pdf,
    extract_text_from_docx
)

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

SKILLS = [
    "python", "sql", "excel", "power bi", "tableau", "java", "c++", "html", "css",
    "javascript", "flask", "django", "react", "node.js", "crm", "sales", "communication",
    "teamwork", "problem solving", "project management", "data analysis", "machine learning",
    "ai", "english", "microsoft office", "word", "outlook"
]



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

