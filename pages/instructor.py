import sqlite3
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# ---------------- DATABASE ---------------- #

conn = sqlite3.connect("database.db", check_same_thread=False)
cursor = conn.cursor()

# ---------------- PAGE CONFIG ---------------- #

st.set_page_config(
    page_title="Instructor Dashboard",
    layout="wide"
)

st.title("📘 Instructor Dashboard")

# ---------------- ACCESS CONTROL ---------------- #

if (
    "logged_in" not in st.session_state
    or not st.session_state.logged_in
    or st.session_state.role != "Instructor"
):
    st.error("Access Denied. Please login again.")
    st.stop()

# ---------------- LOAD DATA ---------------- #

df = pd.read_csv(
    "D:/StudentPerformanceDashboard/data/student_performance.csv"
)

df.columns = df.columns.str.strip()

df.insert(0, "Roll No", range(1, len(df) + 1))

# ---------------- GET SUBJECT FROM LOGIN ---------------- #

subject_input = st.session_state.username.strip().lower()

# ---------------- MATCH SUBJECT SAFELY ---------------- #

matched_subject = None

for col in df.columns:
    if col.lower() == subject_input:
        matched_subject = col
        break

if not matched_subject:
    st.error(
        f"Subject '{subject_input}' not found in dataset."
    )
    st.write("Available subjects:", df.columns.tolist())
    st.stop()

subject_name = matched_subject

# ---------------- LOG VIEW ---------------- #

cursor.execute(
    """
    INSERT INTO teacher_logs (subject, action, login_time)
    VALUES (?, ?, datetime('now','localtime'))
    """,
    (subject_name, "Viewed Subject Dashboard")
)

conn.commit()

# ---------------- SUBJECT HEADER ---------------- #

st.subheader(f"📚 Subject: {subject_name}")

# ---------------- MARKS TABLE ---------------- #

st.subheader("📋 Marks Table")

subject_marks = df[["Roll No", "Name", subject_name]]

st.dataframe(subject_marks)

# ---------------- HISTOGRAM ---------------- #

st.subheader("📊 Distribution")

fig1, ax1 = plt.subplots()

sns.histplot(df[subject_name], kde=True, ax=ax1)

st.pyplot(fig1)

# ---------------- BOXPLOT ---------------- #

st.subheader("📦 Boxplot")

fig2, ax2 = plt.subplots()

sns.boxplot(y=df[subject_name], ax=ax2)

st.pyplot(fig2)

# ---------------- TOP 10 ---------------- #

st.subheader("🏆 Top 10 Students")

top10 = df.sort_values(
    by=subject_name,
    ascending=False
).head(10)

fig3, ax3 = plt.subplots()

bars = ax3.barh(top10["Name"], top10[subject_name])

ax3.invert_yaxis()

for i, bar in enumerate(bars):
    ax3.text(
        bar.get_width() + 1,
        bar.get_y() + bar.get_height() / 2,
        f"{top10[subject_name].iloc[i]:.1f}",
        va="center"
    )

st.pyplot(fig3)

# ---------------- SAVE CHART ---------------- #

os.makedirs("charts", exist_ok=True)

chart_path = f"charts/top10_{subject_name}.png"

fig3.savefig(chart_path, bbox_inches="tight")

# ---------------- DOWNLOAD ---------------- #

st.subheader("⬇ Download Chart")

with open(chart_path, "rb") as file:
    if st.download_button(
        "Download Top 10 Chart",
        file,
        file_name=f"top10_{subject_name}.png",
        mime="image/png"
    ):
        cursor.execute(
            """
            INSERT INTO teacher_logs (subject, action, login_time)
            VALUES (?, ?, datetime('now','localtime'))
            """,
            (subject_name, "Downloaded Chart")
        )
        conn.commit()

        st.success("Downloaded Successfully!")

# ---------------- LOGOUT ---------------- #

st.divider()

if st.button("🚪 Logout"):

    cursor.execute(
        """
        INSERT INTO teacher_logs (subject, action, login_time)
        VALUES (?, ?, datetime('now','localtime'))
        """,
        (subject_name, "Logged Out")
    )

    conn.commit()

    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None
    st.session_state.page = "home"

    st.switch_page("app.py")