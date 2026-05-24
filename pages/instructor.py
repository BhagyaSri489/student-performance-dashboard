import sqlite3
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# ---------------- DATABASE CONNECTION ---------------- #

conn = sqlite3.connect(
    "database.db",
    check_same_thread=False
)

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
    st.error(
        "Access Denied. Please login as Instructor from the main app."
    )
    st.stop()

# ---------------- LOAD DATASET ---------------- #

df = pd.read_csv(
    "D:/StudentPerformanceDashboard/data/student_performance.csv"
)

# Remove extra spaces from column names

df.columns = df.columns.str.strip()

# ---------------- ADD ROLL NUMBER ---------------- #

df.insert(
    0,
    "Roll No",
    range(1, len(df) + 1)
)

# ---------------- GET SUBJECT FROM LOGIN ---------------- #

subject_name = (
    st.session_state.username.capitalize()
)

# ---------------- SUBJECT VALIDATION ---------------- #

if subject_name in df.columns:

    # ---------------- LOG INSTRUCTOR ACTIVITY ---------------- #

    cursor.execute(
        """
        INSERT INTO teacher_logs
        (subject, action)
        VALUES (?, ?)
        """,
        (
            subject_name,
            "Viewed Subject Dashboard"
        )
    )

    conn.commit()

    # ---------------- SUBJECT HEADER ---------------- #

    st.subheader(
        f"📚 {subject_name} Subject Analysis"
    )

    # ---------------- SUBJECT MARKS TABLE ---------------- #

    st.subheader(
        f"📋 Marks for {subject_name}"
    )

    subject_marks = df[
        [
            "Roll No",
            "Name",
            subject_name
        ]
    ].reset_index(drop=True)

    st.dataframe(subject_marks)

    # ---------------- HISTOGRAM ---------------- #

    st.subheader(
        f"📊 Distribution of "
        f"{subject_name} Marks"
    )

    fig1, ax1 = plt.subplots(
        figsize=(8, 4)
    )

    sns.histplot(
        df[subject_name],
        bins=10,
        kde=True,
        color="skyblue",
        ax=ax1
    )

    ax1.set_xlabel("Marks")

    ax1.set_ylabel(
        "Number of Students"
    )

    ax1.set_title(
        f"{subject_name} "
        f"Marks Distribution"
    )

    st.pyplot(fig1)

    # ---------------- BOXPLOT ---------------- #

    st.subheader(
        f"📦 Boxplot for "
        f"{subject_name}"
    )

    fig2, ax2 = plt.subplots(
        figsize=(6, 4)
    )

    sns.boxplot(
        y=df[subject_name],
        color="lightgreen",
        ax=ax2
    )

    ax2.set_title(
        f"{subject_name} "
        f"Score Spread"
    )

    st.pyplot(fig2)

    # ---------------- TOP 10 STUDENTS ---------------- #

    st.subheader(
        f"🏆 Top 10 Students in "
        f"{subject_name}"
    )

    top_students = (
        df.sort_values(
            by=subject_name,
            ascending=False
        )[
            [
                "Roll No",
                "Name",
                subject_name
            ]
        ]
        .head(10)
        .reset_index(drop=True)
    )

    fig3, ax3 = plt.subplots(
        figsize=(10, 6)
    )

    bars = ax3.barh(
        top_students["Name"],
        top_students[subject_name]
    )

    ax3.invert_yaxis()

    ax3.set_xlabel("Marks")

    ax3.set_title(
        f"Top 10 Performers in "
        f"{subject_name}"
    )

    # ---------------- LABELS ---------------- #

    for i, bar in enumerate(bars):

        ax3.text(
            bar.get_width() + 1,
            bar.get_y()
            + bar.get_height() / 2,
            f"{top_students[subject_name][i]:.1f}",
            va="center"
        )

    st.pyplot(fig3)

    # ---------------- SAVE CHART ---------------- #

    os.makedirs(
        "charts",
        exist_ok=True
    )

    chart_path = (
        f"charts/top10_{subject_name}.png"
    )

    fig3.savefig(
        chart_path,
        bbox_inches="tight"
    )

    # ---------------- DOWNLOAD BUTTON ---------------- #

    st.subheader(
        "⬇ Download Top 10 Chart"
    )

    with open(chart_path, "rb") as file:

        if st.download_button(
            label="Download Chart",
            data=file,
            file_name=(
                f"top10_{subject_name}.png"
            ),
            mime="image/png"
        ):

            # ---------------- LOG DOWNLOAD ACTION ---------------- #

            cursor.execute(
                """
                INSERT INTO teacher_logs
                (subject, action)
                VALUES (?, ?)
                """,
                (
                    subject_name,
                    "Downloaded Top 10 Chart"
                )
            )

            conn.commit()

            st.success(
                "Chart Downloaded Successfully!"
            )

# ---------------- SUBJECT NOT FOUND ---------------- #

else:

    st.error(
        f"{subject_name} subject "
        f"not found in dataset."
    )

# ---------------- LOGOUT BUTTON ---------------- #

st.divider()

if st.button("🚪 Logout"):

    # ---------------- LOG LOGOUT ---------------- #

    cursor.execute(
        """
        INSERT INTO teacher_logs
        (subject, action)
        VALUES (?, ?)
        """,
        (
            subject_name,
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