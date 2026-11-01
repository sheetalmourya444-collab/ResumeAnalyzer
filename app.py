import streamlit as st
import re
from pypdf import PdfReader
from docx import Document

st.set_page_config(
    page_title="Resume Analyzer",
    page_icon="📄",
    layout="wide"
)

# ---------------- SKILLS ----------------

SKILLS = {
    "Python", "Java", "C", "C++", "JavaScript",
    "HTML", "CSS", "React", "Node.js", "SQL",
    "MySQL", "MongoDB", "Excel", "Power BI",
    "Tableau", "Pandas", "NumPy", "Matplotlib",
    "Machine Learning", "Deep Learning",
    "Artificial Intelligence", "Data Analysis",
    "Git", "GitHub", "Docker", "AWS", "Azure",
    "Django", "Flask", "FastAPI", "Streamlit",
    "Communication", "Problem Solving",
    "Teamwork", "Leadership"
}

# ---------------- RESUME SECTIONS ----------------

SECTIONS = {
    "Contact Information": r"email|e-mail|phone|mobile|contact|linkedin|github",
    "Education": r"education|academic|degree|b.tech|bachelor|college|university|school",
    "Experience": r"experience|work experience|employment|internship|intern",
    "Skills": r"skills|technical skills|technologies|competencies",
    "Projects": r"projects|project experience",
    "Certifications": r"certifications|certificates|certificate",
    "Summary": r"summary|profile|objective|about me|career objective",
    "Achievements": r"achievements|awards|honors|accomplishments"
}

# ---------------- READ RESUME ----------------

def read_resume(file):

    if file.name.lower().endswith(".pdf"):

        reader = PdfReader(file)

        text = ""

        for page in reader.pages:
            text += (page.extract_text() or "") + "\n"

        return text

    else:

        document = Document(file)

        return "\n".join(
            paragraph.text
            for paragraph in document.paragraphs
        )


# ---------------- SKILL DETECTION ----------------

def find_skills(text):

    text_lower = text.lower()

    detected = []

    for skill in SKILLS:

        if skill.lower() in text_lower:
            detected.append(skill)

    return sorted(set(detected))


# ---------------- SECTION DETECTION ----------------

def find_sections(text):

    text_lower = text.lower()

    found = []

    for section, pattern in SECTIONS.items():

        if re.search(pattern, text_lower):
            found.append(section)

    missing = [
        section
        for section in SECTIONS
        if section not in found
    ]

    return found, missing


# ---------------- CONTACT CHECK ----------------

def check_contacts(text):

    email = bool(
        re.search(
            r"[\w.+-]+@[\w-]+\.[\w.-]+",
            text
        )
    )

    phone = bool(
        re.search(
            r"(?:\+91[-\s]?)?[6-9]\d{9}\b",
            text
        )
    )

    linkedin = "linkedin.com" in text.lower()

    github = "github.com" in text.lower()

    return email, phone, linkedin, github


# ---------------- KEYWORDS ----------------

def extract_words(text):

    stop_words = {
        "the", "and", "for", "with",
        "that", "this", "from",
        "are", "you", "your",
        "have", "has", "will",
        "our", "their", "into",
        "about", "should", "using",
        "candidate", "looking",
        "knowledge", "good",
        "basic", "job", "work"
    }

    words = re.findall(
        r"[a-zA-Z][a-zA-Z0-9+#.-]{2,}",
        text.lower()
    )

    return {
        word
        for word in words
        if word not in stop_words
    }


# ---------------- JOB MATCHING ----------------

def job_match(resume, job):

    if not job.strip():
        return 0, [], []

    resume_words = extract_words(resume)
    job_words = extract_words(job)

    matched = sorted(
        resume_words & job_words
    )

    missing = sorted(
        job_words - resume_words
    )

    score = round(
        len(matched) /
        max(len(job_words), 1)
        * 100
    )

    return score, matched, missing


# ---------------- READABILITY ----------------

def readability_score(text):

    words = text.split()

    sentences = [
        x for x in re.split(
            r"[.!?]+",
            text
        )
        if x.strip()
    ]

    if not words:
        return 0

    average_sentence_length = (
        len(words) /
        max(len(sentences), 1)
    )

    if average_sentence_length <= 18:
        return 90

    elif average_sentence_length <= 25:
        return 75

    elif average_sentence_length <= 35:
        return 60

    else:
        return 45


# ---------------- REPORT ----------------

def create_report(
    ats,
    match,
    readability,
    skills,
    found,
    missing,
    matched,
    missing_keywords,
    suggestions,
    contacts
):

    report = []

    report.append("RESUME ANALYZER REPORT")
    report.append("=" * 30)

    report.append(f"ATS Score: {ats}%")
    report.append(f"Job Match Score: {match}%")
    report.append(f"Readability Score: {readability}%")

    report.append("")
    report.append("Detected Skills:")
    report.append(", ".join(skills) or "None")

    report.append("")
    report.append("Found Sections:")
    report.append(", ".join(found) or "None")

    report.append("")
    report.append("Missing Sections:")
    report.append(", ".join(missing) or "None")

    report.append("")
    report.append("Matched Keywords:")
    report.append(", ".join(matched) or "None")

    report.append("")
    report.append("Missing Keywords:")
    report.append(", ".join(missing_keywords) or "None")

    report.append("")
    report.append("Contact Information:")

    report.append(
        f"Email: {'Yes' if contacts[0] else 'No'}"
    )

    report.append(
        f"Phone: {'Yes' if contacts[1] else 'No'}"
    )

    report.append(
        f"LinkedIn: {'Yes' if contacts[2] else 'No'}"
    )

    report.append(
        f"GitHub: {'Yes' if contacts[3] else 'No'}"
    )

    report.append("")
    report.append("Suggestions:")

    for suggestion in suggestions:
        report.append("- " + suggestion)

    return "\n".join(report)


# ---------------- SIDEBAR ----------------

st.sidebar.title("📄 Upload Resume")

uploaded_file = st.sidebar.file_uploader(
    "Upload your resume",
    type=["pdf", "docx"]
)

st.sidebar.subheader("🎯 Job Matching")

job_description = st.sidebar.text_area(
    "Paste Job Description",
    height=220
)


# ---------------- TITLE ----------------

st.title("📄 Resume Analyzer")

st.write(
    "Analyze your resume using ATS Score, "
    "Skills Detection, Job Matching and "
    "Resume Improvement Suggestions."
)


# ---------------- NO FILE ----------------

if not uploaded_file:

    st.info(
        "👈 Upload your PDF or DOCX resume "
        "from the sidebar."
    )

    st.stop()


# ---------------- READ FILE ----------------

try:

    resume_text = read_resume(uploaded_file)

except Exception as error:

    st.error(
        f"Could not read resume: {error}"
    )

    st.stop()


if not resume_text.strip():

    st.error(
        "No readable text found in this file."
    )

    st.stop()


# ---------------- ANALYSIS ----------------

detected_skills = find_skills(
    resume_text
)

found_sections, missing_sections = find_sections(
    resume_text
)

contact_info = check_contacts(
    resume_text
)

job_score, matched_keywords, missing_keywords = job_match(
    resume_text,
    job_description
)

readability = readability_score(
    resume_text
)


# ---------------- ATS SCORE ----------------

ats_score = 0

if contact_info[0]:
    ats_score += 10

if contact_info[1]:
    ats_score += 10

if contact_info[2]:
    ats_score += 5

if contact_info[3]:
    ats_score += 5

ats_score += min(
    len(found_sections) * 5,
    40
)

ats_score += min(
    len(detected_skills) * 2,
    20
)

word_count = len(
    resume_text.split()
)

if 250 <= word_count <= 900:

    ats_score += 10

elif word_count >= 150:

    ats_score += 5

ats_score = min(
    ats_score,
    100
)

# ---------------- SMART RESUME ANALYSIS ----------------

strengths = []
weaknesses = []

# Strength checks
if ats_score >= 70:
    strengths.append("Strong ATS-friendly resume structure.")

if len(detected_skills) >= 5:
    strengths.append("Good number of relevant skills detected.")

if contact_info[0] and contact_info[1]:
    strengths.append("Email and phone number are available.")

if contact_info[2]:
    strengths.append("LinkedIn profile is included.")

if contact_info[3]:
    strengths.append("GitHub profile is included.")

if len(found_sections) >= 5:
    strengths.append("Resume contains most important sections.")

if readability >= 75:
    strengths.append("Resume has good readability.")

# Weakness checks
if ats_score < 70:
    weaknesses.append("ATS score can be improved.")

if len(detected_skills) < 5:
    weaknesses.append("Add more relevant technical skills.")

if not contact_info[2]:
    weaknesses.append("LinkedIn profile is missing.")

if not contact_info[3]:
    weaknesses.append("GitHub profile is missing.")

if len(missing_sections) > 0:
    weaknesses.append(
        "Some important resume sections are missing."
    )

if readability < 75:
    weaknesses.append(
        "Resume readability can be improved."
    )

if job_description.strip() and job_score < 60:
    weaknesses.append(
        "Resume has a low match with the provided job description."
    )

# Display Smart Analysis
st.subheader("🤖 Smart Resume Analysis")

analysis_left, analysis_right = st.columns(2)

with analysis_left:

    st.markdown("### 💪 Resume Strengths")

    if strengths:
        for strength in strengths:
            st.success(strength)
    else:
        st.info("No major strengths detected yet.")

with analysis_right:

    st.markdown("### ⚠️ Areas to Improve")

    if weaknesses:
        for weakness in weaknesses:
            st.warning(weakness)
    else:
        st.success("No major weaknesses detected.")
        # ---------------- OVERALL RESUME RATING ----------------

overall_score = round(
    (ats_score + job_score + readability) / 3
)

st.subheader("⭐ Overall Resume Rating")

st.progress(
    overall_score / 100,
    text=f"Overall Resume Score: {overall_score}%"
)

if overall_score >= 80:
    st.success("Excellent Resume ⭐")
elif overall_score >= 60:
    st.info("Good Resume 👍")
elif overall_score >= 40:
    st.warning("Average Resume — Improvement Needed")
else:
    st.error("Resume Needs Major Improvement") 
    # ---------------- SKILL GAP ANALYSIS ----------------

st.subheader("🎯 Skill Gap Analysis")

if job_description.strip():
    if missing_keywords:
        st.write("Skills/Keywords to Improve:")
        for keyword in missing_keywords[:10]:
            st.warning(f"• {keyword}")
    else:
        st.success("Great! No major skill gaps found.")
else:
    st.info(
        "Add a Job Description to see personalized Skill Gap Analysis."
    )
    # ---------------- PERSONALIZED RECOMMENDATIONS ----------------

st.subheader("💡 Personalized Recommendations")

recommendations = []

if ats_score < 70:
    recommendations.append(
        "Improve your resume structure and ATS compatibility."
    )

if len(detected_skills) < 5:
    recommendations.append(
        "Add more relevant technical skills that you actually know."
    )

if not contact_info[2]:
    recommendations.append(
        "Add your LinkedIn profile to improve your professional presence."
    )

if not contact_info[3]:
    recommendations.append(
        "Add your GitHub profile if you have coding projects."
    )

if readability < 75:
    recommendations.append(
        "Use shorter sentences and clear bullet points."
    )

if job_description.strip() and job_score < 60:
    recommendations.append(
        "Customize your resume according to the job description."
    )

if not recommendations:
    recommendations.append(
        "Your resume is performing well. Keep tailoring it for each job."
    )

for recommendation in recommendations:
    st.info("👉 " + recommendation)
    # ---------------- SCORE SUMMARY ----------------

st.subheader("📊 Resume Score Summary")

summary_col1, summary_col2, summary_col3 = st.columns(3)

summary_col1.metric(
    "ATS Score",
    f"{ats_score}%"
)

summary_col2.metric(
    "Job Match",
    f"{job_score}%"
)

summary_col3.metric(
    "Overall Score",
    f"{overall_score}%"
)
# ---------------- IMPROVEMENT CHECKLIST ----------------

st.subheader("📌 Resume Improvement Checklist")

checklist = []

checklist.append(
    ("Email", "Present" if contact_info[0] else "Missing")
)

checklist.append(
    ("Phone", "Present" if contact_info[1] else "Missing")
)

checklist.append(
    ("LinkedIn", "Present" if contact_info[2] else "Missing")
)

checklist.append(
    ("GitHub", "Present" if contact_info[3] else "Missing")
)

checklist.append(
    ("Skills", "Good" if len(detected_skills) >= 5 else "Needs Improvement")
)

checklist.append(
    ("Readability", "Good" if readability >= 75 else "Needs Improvement")
)

for item, status in checklist:
    if status in ["Present", "Good"]:
        st.success(f"✅ {item}: {status}")
    else:
        st.warning(f"⚠️ {item}: {status}")
        
# ---------------- SUGGESTIONS ----------------

suggestions = []


if not contact_info[0]:

    suggestions.append(
        "Add a professional email address."
    )


if not contact_info[1]:

    suggestions.append(
        "Add a valid phone number."
    )


if not contact_info[2]:

    suggestions.append(
        "Add your LinkedIn profile."
    )


if not contact_info[3] and (
    "python" in resume_text.lower()
    or "developer" in resume_text.lower()
):

    suggestions.append(
        "Add GitHub if you have coding projects."
    )


if "Achievements" in missing_sections:

    suggestions.append(
        "Add an Achievements/Awards section if relevant."
    )


if "Summary" in missing_sections:

    suggestions.append(
        "Add a short professional summary."
    )


if len(detected_skills) < 5:

    suggestions.append(
        "Add relevant skills that you genuinely possess."
    )


if job_description.strip() and missing_keywords:

    suggestions.append(
        "Add relevant missing job keywords "
        "only when they accurately describe your experience."
    )


if not suggestions:

    suggestions.append(
        "Your resume has a strong structure. "
        "Continue tailoring it for each job."
    )


# ---------------- TOP METRICS ----------------

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "ATS Score",
    f"{ats_score}%"
)

col2.metric(
    "Job Match",
    f"{job_score}%"
)

col3.metric(
    "Skills Found",
    len(detected_skills)
)

col4.metric(
    "Readability",
    f"{readability}%"
)


st.progress(
    ats_score / 100,
    text=f"ATS Score: {ats_score}%"
)


# ---------------- SECTIONS ----------------

left, right = st.columns(2)


with left:

    st.subheader(
        "✅ Found Sections"
    )

    for section in found_sections:

        st.write(
            "✓",
            section
        )


with right:

    st.subheader(
        "❌ Missing Sections"
    )

    for section in missing_sections:

        st.write(
            "•",
            section
        )


# ---------------- SKILLS ----------------

st.subheader(
    "🛠️ Detected Skills"
)

if detected_skills:

    st.write(
        " • ".join(
            detected_skills
        )
    )

else:

    st.write(
        "No common skills detected."
    )


# ---------------- CONTACT ----------------

st.subheader(
    "📞 Contact Information"
)

c1, c2, c3, c4 = st.columns(4)


c1.metric(
    "Email",
    "Found" if contact_info[0]
    else "Missing"
)

c2.metric(
    "Phone",
    "Found" if contact_info[1]
    else "Missing"
)

c3.metric(
    "LinkedIn",
    "Found" if contact_info[2]
    else "Missing"
)

c4.metric(
    "GitHub",
    "Found" if contact_info[3]
    else "Missing"
)


# ---------------- JOB MATCHING ----------------

if job_description.strip():

    st.subheader(
        "🎯 Job Matching"
    )

    st.progress(
        job_score / 100,
        text=f"Job Match Score: {job_score}%"
    )

    match_left, match_right = st.columns(2)


    with match_left:

        st.markdown(
            "### ✅ Matched Keywords"
        )

        if matched_keywords:

            st.write(
                ", ".join(matched_keywords)
            )
            # ---------------- ANALYTICS DASHBOARD ----------------

st.subheader("📊 Analytics Dashboard")

# Overall Score Chart
st.markdown("### 📈 Resume Performance")

score_data = {
    "Metric": [
        "ATS Score",
        "Job Match",
        "Readability"
    ],
    "Score": [
        ats_score,
        job_score,
        readability
    ]
}

st.bar_chart(
    score_data,
    x="Metric",
    y="Score"
)

# Resume Sections Analysis
st.markdown("### 📋 Resume Sections Analysis")

section_data = {
    "Status": ["Found", "Missing"],
    "Count": [
        len(found_sections),
        len(missing_sections)
    ]
}

st.bar_chart(
    section_data,
    x="Status",
    y="Count"
)

# Contact Information Analysis
st.markdown("### 📞 Contact Information Analysis")

contact_data = {
    "Contact": [
        "Email",
        "Phone",
        "LinkedIn",
        "GitHub"
    ],
    "Status": [
        1 if contact_info[0] else 0,
        1 if contact_info[1] else 0,
        1 if contact_info[2] else 0,
        1 if contact_info[3] else 0
    ]
}

st.bar_chart(
    contact_data,
    x="Contact",
    y="Status"
)

# Skills Overview
st.markdown("### 🛠️ Skills Overview")

st.metric(
    "Total Skills Detected",
    len(detected_skills)
)

if detected_skills:
    st.write(
        ", ".join(detected_skills)
    )
else:
    st.info("No skills detected.")