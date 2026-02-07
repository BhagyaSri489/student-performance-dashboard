import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report
import os
st.set_page_config(page_title="Student Dashboard", layout="wide")
st.title("Student Dashboard")
# Access Control
if "registered" not in st.session_state or not st.session_state.registered or st.session_state.role != "Student":
    st.error("Access Denied. Please register/login as Student from the main app.")
    st.stop()
# Load dataset
df = pd.read_csv("D:/StudentPerformanceDashboard/data/student_performance.csv")
# Strip whitespace from column names
df.columns = df.columns.str.strip()
df.insert(0, "Roll No", range(1, len(df) + 1))
numeric_subjects = [
    col for col in df.select_dtypes(include=np.number).columns
    if col not in ["Attendance (%)", "Roll No"]
]
# Student Selection
student_name = st.text_input("Enter Student Name").strip()
if st.button("Submit"):
    student_data = df[df["Name"].str.lower() == student_name.lower()]
    if not student_data.empty:
        # Subject Marks
        st.subheader("Subject Marks")
        marks = student_data[numeric_subjects].T
        marks.columns = ["Marks"]
        st.bar_chart(marks)
        # Attendance
        if "Attendance (%)" in df.columns:
            st.metric("Attendance", f"{student_data['Attendance (%)'].values[0]:.2f}%")
        else:
            st.info("Attendance data not available.")
        # Position
        total_marks = df[numeric_subjects].sum(axis=1)
        student_total = student_data[numeric_subjects].sum(axis=1).values[0]
        position = total_marks.rank(ascending=False)[student_data.index[0]]
        st.metric("Position", f"{int(position)} out of {len(df)}")
        # Remarks
        if "Remarks" in student_data.columns:
            st.subheader("Remarks")
            st.info(student_data["Remarks"].values[0])
        # GPA Calculator
        st.subheader("GPA Calculator")
        gpa = (student_data[numeric_subjects].mean(axis=1).values[0] / 100) * 4
        st.metric("GPA", f"{gpa:.2f} / 4.0")
        # Performance Classification
        st.subheader("Performance Classification")
        df["Performance"] = np.where(df[numeric_subjects].mean(axis=1) > 75, "High", "Low")
        st.code(classification_report(df["Performance"], df["Performance"]))
        # Subject-wise Contribution Pie Chart
        st.subheader("Subject-wise Contribution")
        subject_scores = student_data[numeric_subjects].iloc[0]
        fig, ax = plt.subplots()
        ax.pie(subject_scores,labels=subject_scores.index, autopct="%1.1f%%", startangle=140)
        ax.set_title(f"Subject Contribution for {student_name}")
        st.pyplot(fig)
        # Download Pie Chart
        st.subheader("Download Pie Chart")
        chart_path = f"charts/pie_subject_contribution_{student_name.replace(' ', '_')}.png"
        os.makedirs("charts", exist_ok=True)
        fig.savefig(chart_path, bbox_inches="tight")
        with open(chart_path, "rb") as file:
            st.download_button(
                label="Download Pie Chart",
                data=file,
                file_name=os.path.basename(chart_path),
                mime="image/png"
            )
    else:
        st.error("Student not found.")
