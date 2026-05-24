import sqlite3
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report
import os

# ---------------- PAGE CONFIG ---------------- #

st.set_page_config(
    page_title="Student Dashboard",
    layout="wide"
)

st.title("🎓 Student Dashboard")

# ---------------- DATABASE CONNECTION ---------------- #

conn = sqlite3.connect(
    "database.db",
    check_same_thread=False
)

cursor = conn.cursor()

# ---------------- ACCESS CONTROL ---------------- #

if (
    "logged_in" not in st.session_state
    or not st.session_state.logged_in
    or st.session_state.role != "Student"
):
    st.error(
        "Access Denied. Please login from the main app."
    )
    st.stop()

# ---------------- LOAD CSV DATA ---------------- #

df = pd.read_csv(
    "D:/StudentPerformanceDashboard/data/student_performance.csv"
)

# Remove extra spaces from columns

df.columns = df.columns.str.strip()

# ---------------- GET LOGGED-IN STUDENT ---------------- #

student_name = st.session_state.username

# ---------------- FIND STUDENT ---------------- #

student_data = df[
    df["Name"].str.lower()
    ==
    student_name.lower()
]

# ---------------- STUDENT CHECK ---------------- #

if student_data.empty:

    st.error(
        "Student not found in dataset."
    )

    st.stop()

# ---------------- LOG DASHBOARD VIEW ---------------- #

cursor.execute(
    """
    INSERT INTO student_logs
    (student_name, action)
    VALUES (?, ?)
    """,
    (
        student_name,
        "Viewed Dashboard"
    )
)

conn.commit()

# ---------------- WELCOME MESSAGE ---------------- #

st.success(
    f"Welcome {student_name}"
)

# ---------------- ADD ROLL NUMBER ---------------- #

df.insert(
    0,
    "Roll No",
    range(1, len(df) + 1)
)

# ---------------- NUMERIC SUBJECTS ---------------- #

numeric_subjects = [

    col for col in df.select_dtypes(
        include=np.number
    ).columns

    if col not in [
        "Roll No",
        "Attendance (%)"
    ]
]

# ---------------- STUDENT DETAILS ---------------- #

st.subheader("📋 Student Details")

st.dataframe(student_data)

# ---------------- SUBJECT MARKS ---------------- #

st.subheader("📊 Subject Marks")

marks = student_data[
    numeric_subjects
].T

marks.columns = ["Marks"]

st.bar_chart(marks)

# ---------------- ATTENDANCE ---------------- #

if "Attendance (%)" in df.columns:

    attendance = student_data[
        "Attendance (%)"
    ].values[0]

    st.metric(
        "Attendance",
        f"{attendance:.2f}%"
    )

# ---------------- TOTAL MARKS ---------------- #

student_total = (
    student_data[numeric_subjects]
    .sum(axis=1)
    .values[0]
)

st.metric(
    "Total Marks",
    f"{student_total:.2f}"
)

# ---------------- AVERAGE SCORE ---------------- #

average_score = (
    student_data[numeric_subjects]
    .mean(axis=1)
    .values[0]
)

st.metric(
    "Average Score",
    f"{average_score:.2f}"
)

# ---------------- GPA CALCULATOR ---------------- #

st.subheader("🎯 GPA Calculator")

gpa = (
    average_score / 100
) * 4

st.metric(
    "GPA",
    f"{gpa:.2f} / 4.0"
)

# ---------------- CLASS POSITION ---------------- #

total_marks_all = (
    df[numeric_subjects]
    .sum(axis=1)
)

position = total_marks_all.rank(
    ascending=False
)[student_data.index[0]]

st.metric(
    "Class Position",
    f"{int(position)} out of {len(df)}"
)

# ---------------- PERFORMANCE CLASSIFICATION ---------------- #

st.subheader(
    "📈 Performance Classification"
)

df["Performance"] = np.where(
    df[numeric_subjects]
    .mean(axis=1) > 75,
    "High",
    "Low"
)

report = classification_report(
    df["Performance"],
    df["Performance"]
)

st.code(report)

# ---------------- REMARKS ---------------- #

if "Remarks" in student_data.columns:

    st.subheader("📝 Remarks")

    st.info(
        student_data["Remarks"]
        .values[0]
    )

# ---------------- PIE CHART ---------------- #

st.subheader(
    "🥧 Subject-wise Contribution"
)

subject_scores = student_data[
    numeric_subjects
].iloc[0]

fig, ax = plt.subplots()

ax.pie(
    subject_scores,
    labels=subject_scores.index,
    autopct="%1.1f%%",
    startangle=140
)

ax.set_title(
    f"Subject Contribution for "
    f"{student_name}"
)

st.pyplot(fig)

# ---------------- SAVE CHART ---------------- #

os.makedirs(
    "charts",
    exist_ok=True
)

chart_path = (
    f"charts/"
    f"{student_name.replace(' ', '_')}_pie_chart.png"
)

fig.savefig(
    chart_path,
    bbox_inches="tight"
)

# ---------------- DOWNLOAD BUTTON ---------------- #

st.subheader("⬇ Download Pie Chart")

with open(chart_path, "rb") as file:

    if st.download_button(
        label="Download Pie Chart",
        data=file,
        file_name=os.path.basename(
            chart_path
        ),
        mime="image/png"
    ):

        # ---------------- LOG DOWNLOAD ---------------- #

        cursor.execute(
            """
            INSERT INTO student_logs
            (student_name, action)
            VALUES (?, ?)
            """,
            (
                student_name,
                "Downloaded Pie Chart"
            )
        )

        conn.commit()

        st.success(
            "Chart Downloaded Successfully!"
        )

# ---------------- LOGOUT BUTTON ---------------- #

st.divider()

if st.button("🚪 Logout"):

    # ---------------- LOG LOGOUT ---------------- #

    cursor.execute(
        """
        INSERT INTO student_logs
        (student_name, action)
        VALUES (?, ?)
        """,
        (
            student_name,
            "Logged Out"
        )
    )

    conn.commit()

    # ---------------- CLEAR SESSION ---------------- #

    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None
    st.session_state.page = "home"

    st.switch_page("app.py")