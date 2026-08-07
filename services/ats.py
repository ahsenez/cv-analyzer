from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

SKILLS = [
    "python", "sql", "excel", "power bi", "tableau",
    "java", "c++", "html", "css", "javascript",
    "flask", "django", "react", "node.js",
    "crm", "sales", "communication",
    "teamwork", "problem solving",
    "project management",
    "data analysis",
    "machine learning",
    "ai",
    "english",
    "microsoft office",
    "word",
    "outlook"
]


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

    sections = [
        "experience",
        "education",
        "skills",
        "summary",
        "profile"
    ]

    found_sections = sum(
        1 for section in sections
        if section in cv_text_lower
    )

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
