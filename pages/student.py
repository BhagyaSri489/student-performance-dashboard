import sqlite3
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from sklearn.metrics import classification_report

# ---------------- PAGE CONFIG ---------------- #

st.set_page_config(
    page_title="Student Dashboard",
    layout="wide"
)

st.title("🎓 Student Dashboard")

# ---------------- DATABASE ---------------- #

conn = sqlite3.connect("database.db", check_same_thread=False)
cursor = conn.cursor()

# ---------------- ACCESS CONTROL ---------------- #

if (
    "logged_in" not in st.session_state
    or not st.session_state.logged_in
    or st.session_state.role != "Student"
):
    st.error("Access Denied. Please login from main app.")
    st.stop()

# ---------------- LOAD DATA ---------------- #

df = pd.read_csv(
    "data/student_performance.csv"
)

df.columns = df.columns.str.strip()

student_name = st.session_state.username

student_data = df[
    df["Name"].str.lower() == student_name.lower()
]

if student_data.empty:
    st.error("Student not found in dataset.")
    st.stop()

# ---------------- ONE-TIME LOGIN LOG (FIXED) ---------------- #

if "student_logged" not in st.session_state:

    cursor.execute(
        """
        INSERT INTO student_logs (student_name, action, login_time)
        VALUES (?, ?, datetime('now','localtime'))
        """,
        (student_name, "Viewed Dashboard")
    )

    conn.commit()

    st.session_state.student_logged = True

# ---------------- WELCOME ---------------- #

st.success(f"Welcome {student_name}")

# ---------------- ROLL NUMBER ---------------- #

df.insert(0, "Roll No", range(1, len(df) + 1))

# ---------------- SUBJECTS ---------------- #

numeric_subjects = [
    col for col in df.select_dtypes(include=np.number).columns
    if col not in ["Roll No", "Attendance (%)"]
]

# ---------------- STUDENT DETAILS ---------------- #

st.subheader("📋 Student Details")
st.dataframe(student_data)

# ---------------- MARKS ---------------- #

st.subheader("📊 Subject Marks")

marks = student_data[numeric_subjects].T
marks.columns = ["Marks"]

st.bar_chart(marks)

# ---------------- ATTENDANCE ---------------- #

if "Attendance (%)" in df.columns:
    attendance = student_data["Attendance (%)"].values[0]
    st.metric("Attendance", f"{attendance:.2f}%")

# ---------------- TOTAL ---------------- #

total_marks = student_data[numeric_subjects].sum(axis=1).values[0]
st.metric("Total Marks", f"{total_marks:.2f}")

# ---------------- AVERAGE ---------------- #

avg_score = student_data[numeric_subjects].mean(axis=1).values[0]
st.metric("Average Score", f"{avg_score:.2f}")

# ---------------- GPA ---------------- #

gpa = (avg_score / 100) * 4
st.metric("GPA", f"{gpa:.2f} / 4.0")

# ---------------- CLASS POSITION ---------------- #

total_all = df[numeric_subjects].sum(axis=1)
rank = total_all.rank(ascending=False)[student_data.index[0]]

st.metric("Class Position", f"{int(rank)} out of {len(df)}")

# ---------------- PERFORMANCE ---------------- #

df["Performance"] = np.where(
    df[numeric_subjects].mean(axis=1) > 75,
    "High",
    "Low"
)

st.subheader("📈 Performance Report")

report = classification_report(
    df["Performance"],
    df["Performance"]
)

st.code(report)

# ---------------- REMARKS ---------------- #

if "Remarks" in student_data.columns:
    st.subheader("📝 Remarks")
    st.info(student_data["Remarks"].values[0])

# ---------------- PIE CHART ---------------- #

st.subheader("🥧 Subject Contribution")

subject_scores = student_data[numeric_subjects].iloc[0]

fig, ax = plt.subplots()

ax.pie(
    subject_scores,
    labels=subject_scores.index,
    autopct="%1.1f%%",
    startangle=140
)

ax.set_title(f"Subject Contribution - {student_name}")

st.pyplot(fig)

# ---------------- SAVE CHART ---------------- #

os.makedirs("charts", exist_ok=True)

chart_path = f"charts/{student_name.replace(' ', '_')}_pie.png"

fig.savefig(chart_path, bbox_inches="tight")

# ---------------- DOWNLOAD ---------------- #

st.subheader("⬇ Download Chart")

with open(chart_path, "rb") as file:
    if st.download_button(
        "Download Pie Chart",
        file,
        file_name=os.path.basename(chart_path),
        mime="image/png"
    ):
        cursor.execute(
            """
            INSERT INTO student_logs (student_name, action, login_time)
            VALUES (?, ?, datetime('now','localtime'))
            """,
            (student_name, "Downloaded Pie Chart")
        )

        conn.commit()

        st.success("Chart Downloaded Successfully!")

# ---------------- LOGOUT (FIXED SESSION RESET) ---------------- #

st.divider()

if st.button("🚪 Logout"):

    cursor.execute(
        """
        INSERT INTO student_logs (student_name, action, login_time)
        VALUES (?, ?, datetime('now','localtime'))
        """,
        (student_name, "Logged Out")
    )

    conn.commit()

    # reset session safely
    for key in list(st.session_state.keys()):
        del st.session_state[key]

    st.switch_page("app.py")