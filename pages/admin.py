import sqlite3
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler
import io
import subprocess

# ---------------- DATABASE CONNECTION ---------------- #

conn = sqlite3.connect(
    "database.db",
    check_same_thread=False
)

cursor = conn.cursor()

# ---------------- PAGE CONFIG ---------------- #

st.set_page_config(
    page_title="Admin Dashboard",
    layout="wide"
)

st.title("🛠 Admin Dashboard")

# ---------------- ACCESS CONTROL ---------------- #

if (
    "logged_in" not in st.session_state
    or not st.session_state.logged_in
    or st.session_state.role != "Admin"
):
    st.error("Access Denied. Please login as Admin from the main app.")
    st.stop()

# ---------------- ADMIN VIEW LOG ---------------- #

cursor.execute(
    """
    INSERT INTO admin_logs (admin_name, action, login_time)
    VALUES (?, ?, datetime('now','localtime'))
    """,
    ("admin", "Viewed Dashboard")
)

conn.commit()

# ---------------- LOAD DATA ---------------- #

df = pd.read_csv(
    "D:/StudentPerformanceDashboard/data/student_performance.csv"
)

df.columns = df.columns.str.strip()

df.insert(0, "Roll No", range(1, len(df) + 1))

numeric_subjects = df.select_dtypes(include=np.number).columns.tolist()

if "Roll No" in numeric_subjects:
    numeric_subjects.remove("Roll No")

# ---------------- SIDEBAR MENU ---------------- #

menu = st.sidebar.radio(
    "📌 Choose Section",
    ["📊 Analytics Dashboard", "📜 System Logs"]
)

# ===================================================== #
#               ANALYTICS DASHBOARD
# ===================================================== #

if menu == "📊 Analytics Dashboard":

    st.sidebar.header("Filters")

    student_filter = st.sidebar.multiselect(
        "Filter by Student(s)",
        df["Name"].unique()
    )

    subject_filter = st.sidebar.multiselect(
        "Filter by Subject(s)",
        numeric_subjects
    )

    filtered_df = df.copy()

    if student_filter:
        filtered_df = filtered_df[
            filtered_df["Name"].isin(student_filter)
        ]

    if subject_filter:
        filtered_df = filtered_df[
            ["Roll No", "Name"] + subject_filter
        ]

    st.subheader("📋 Filtered Data")
    st.dataframe(filtered_df)

    st.subheader("📊 Subject-wise Average Marks")

    avg_scores = df[numeric_subjects].mean().sort_values(ascending=False)

    fig, ax = plt.subplots(figsize=(10, 5))

    sns.barplot(
        x=avg_scores.index,
        y=avg_scores.values,
        ax=ax
    )

    plt.xticks(rotation=45)

    st.pyplot(fig)

    if "Attendance (%)" in df.columns:

        st.subheader("📅 Attendance Overview")

        st.metric(
            "Average Attendance",
            f"{df['Attendance (%)'].mean():.2f}%"
        )

        st.line_chart(df["Attendance (%)"])

    st.subheader("📈 Summary Statistics")
    st.dataframe(df[numeric_subjects].describe())

    scaler = MinMaxScaler()

    scaled_array = scaler.fit_transform(df[numeric_subjects])

    scaled_df = pd.DataFrame(
        scaled_array * 100,
        columns=numeric_subjects
    ).round(2)

    scaled_df.insert(0, "Roll No", df["Roll No"])
    scaled_df.insert(1, "Name", df["Name"])

    st.subheader("⚙ Normalized Scores")
    st.dataframe(scaled_df)

    st.subheader("🏆 Leaderboard")

    leaderboard = df.sort_values(
        by="Total Marks",
        ascending=False
    )[["Name", "Total Marks", "Average Score"]]

    st.table(leaderboard.head(10))

    st.subheader("⬇ Export Data")

    csv = filtered_df.to_csv(index=False).encode("utf-8")

    if st.download_button(
        "Download CSV",
        csv,
        "filtered.csv",
        "text/csv"
    ):
        cursor.execute(
            """
            INSERT INTO admin_logs (admin_name, action, login_time)
            VALUES (?, ?, datetime('now','localtime'))
            """,
            ("admin", "Downloaded CSV")
        )
        conn.commit()

# ===================================================== #
#                    SYSTEM LOGS
# ===================================================== #

elif menu == "📜 System Logs":

    st.subheader("📜 System Logs (Live)")

    # ---------------- LOG CONTROLS ---------------- #

    st.markdown("### 🧹 Log Management")

    col1, col2, col3, col4 = st.columns(4)

    # 🔄 Refresh logs
    with col1:
        if st.button("🔄 Refresh Logs"):
            st.rerun()

    # 🗑 Student logs
    with col2:
        if st.button("🗑 Student Logs"):
            subprocess.run(["python", "reset_logs.py", "student"])
            st.success("Student logs deleted!")
            st.rerun()

    # 🗑 Instructor logs
    with col3:
        if st.button("🗑 Instructor Logs"):
            subprocess.run(["python", "reset_logs.py", "teacher"])
            st.success("Instructor logs deleted!")
            st.rerun()

    # 🗑 Admin logs
    with col4:
        if st.button("🗑 Admin Logs"):
            subprocess.run(["python", "reset_logs.py", "admin"])
            st.success("Admin logs deleted!")
            st.rerun()

    # 🧨 DELETE ALL LOGS
    if st.button("🧨 Delete ALL Logs"):
        subprocess.run(["python", "reset_logs.py", "all"])
        st.success("All logs deleted!")
        st.rerun()

    # ---------------- TABLES ---------------- #

    st.markdown("### 📘 Student Logs")
    student_logs = pd.read_sql_query(
        "SELECT * FROM student_logs ORDER BY login_time DESC",
        conn
    )
    st.dataframe(student_logs, use_container_width=True)

    st.markdown("### 📚 Instructor Logs")
    teacher_logs = pd.read_sql_query(
        "SELECT * FROM teacher_logs ORDER BY login_time DESC",
        conn
    )
    st.dataframe(teacher_logs, use_container_width=True)

    st.markdown("### 🛠 Admin Logs")
    admin_logs = pd.read_sql_query(
        "SELECT * FROM admin_logs ORDER BY login_time DESC",
        conn
    )
    st.dataframe(admin_logs, use_container_width=True)

# ---------------- LOGOUT ---------------- #

st.divider()

if st.button("🚪 Logout"):

    cursor.execute(
        """
        INSERT INTO admin_logs (admin_name, action, login_time)
        VALUES (?, ?, datetime('now','localtime'))
        """,
        ("admin", "Logged Out")
    )
    conn.commit()

    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None
    st.session_state.page = "home"

    st.switch_page("app.py")