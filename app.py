import streamlit as st
import pandas as pd
import joblib
from report_generator import generate_pdf

# ---------------------------------
# PAGE CONFIG
# ---------------------------------
st.set_page_config(
    page_title="Dropout Risk Predictor",
    layout="wide"
)

# Load CSS
with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Load Model
model = joblib.load("best_drop_out_model.pkl")

# TITLE
st.markdown("""
    <h1>🎓 Student Dropout Risk Prediction</h1>
    <p>Enter student information to assess dropout likelihood.</p>
""", unsafe_allow_html=True)

# ---------- STUDENT INPUT UI ----------
with st.container():

    student_name = st.text_input("Student Name")

    # UPDATED Numerical Features — FINAL Features Used in Model
    stress_level = st.slider("Stress Level (1-10)", 1, 10, 5)
    motivation_level = st.slider("Motivation Level (1-10)", 1, 10, 5)
    exam_anxiety_score = st.slider("Exam Anxiety Score (1-10)", 1, 10, 5)
    previous_gpa = st.slider("Previous GPA (1–4 Scale)", 1.0, 4.0, 3.0)
    exam_score = st.slider("Latest Exam Score (0-100)", 0, 100, 75)
    mental_health_rating = st.slider("Mental Health Rating (1-10)", 1, 10, 6)
    exercise_frequency = st.slider("Exercise Frequency (Days per Week)", 0, 7, 3)
    sleep_hours = st.slider("Sleep Hours Per Day", 0, 12, 7)
    attendance_percentage = st.slider("Attendance Percentage (%)", 0, 100, 85)

    # Categorical Features (UNCHANGED)
    parental_education_level = st.selectbox("Parental Education Level",
        ["High School", "Some College", "Bachelor", "Master", "PhD"])

    major = st.selectbox("Major",
        ["Engineering", "Computer Science", "Biology", "Arts", "Psychology", "Business"])

    study_environment = st.selectbox("Study Environment",
        ["Café", "Co-Learning Group", "Dorm", "Library", "Quiet Room"])

    diet_quality = st.selectbox("Diet Quality", ["Poor", "Fair", "Good"])
    learning_style = st.selectbox("Learning Style",
        ["Visual", "Auditory", "Reading", "Kinesthetic"])
    family_income_range = st.selectbox("Family Income Range", ["Low", "Medium", "High"])
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])

# Updated DataFrame with FINAL model features
user_input = pd.DataFrame([{
    "student_name": student_name,
    "stress_level": stress_level,
    "motivation_level": motivation_level,
    "exam_anxiety_score": exam_anxiety_score,
    "previous_gpa": previous_gpa,
    "exam_score": exam_score,
    "mental_health_rating": mental_health_rating,
    "exercise_frequency": exercise_frequency,
    "sleep_hours": sleep_hours,
    "attendance_percentage": attendance_percentage,
    "parental_education_level": parental_education_level,
    "major": major,
    "study_environment": study_environment,
    "diet_quality": diet_quality,
    "learning_style": learning_style,
    "family_income_range": family_income_range,
    "gender": gender
}])

# ---------- PREDICTION ----------
if st.button("Predict Dropout Risk"):

    if student_name.strip() == "":
        st.warning("Please enter the Student Name before predicting 🚨")
        st.stop()

    probability = model.predict_proba(user_input.drop(columns=["student_name"]))[0][1]
    probability = round(probability, 2)
    percent = int(probability * 100)

    if probability >= 0.7:
        risk_message = "🚨 HIGH Risk — Immediate Intervention Required!"
        gauge_color = "#D7263D"
    elif probability >= 0.3:
        risk_message = "⚠️ MEDIUM Risk — Provide Extra Support and Guidance."
        gauge_color = "#F5A623"
    else:
        risk_message = "👍 LOW Risk — Student is Doing Well!"
        gauge_color = "#00FF85"

    st.markdown(f"""
        <div class="result-card">
            <div class="result-title">Dropout Risk</div>
            <div class="result-score">{percent}%</div>
            <div class="risk-text">{risk_message}</div>
        </div>
    """, unsafe_allow_html=True)

    gauge_width = max(probability * 100, 5)

    st.markdown(f"""
        <div class="gauge-container">
            <div class="gauge" style="width:{gauge_width}%; background:{gauge_color};"></div>
        </div>
    """, unsafe_allow_html=True)

    # PDF REPORT DOWNLOAD
    pdf_buffer = generate_pdf(user_input.iloc[0].to_dict(), percent, risk_message)

    st.download_button(
        label="📄 Download Report",
        data=pdf_buffer,
        file_name=f"{student_name}_dropout_risk_report.pdf",
        mime="application/pdf",
    )
