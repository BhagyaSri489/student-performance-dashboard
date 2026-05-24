import sqlite3
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler
import io

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
    st.error(
        "Access Denied. Please login as Admin from the main app."
    )
    st.stop()

# ---------------- ADMIN LOGIN LOG ---------------- #

cursor.execute(
    """
    INSERT INTO admin_logs
    (admin_name, action)
    VALUES (?, ?)
    """,
    (
        "admin",
        "Viewed Dashboard"
    )
)

conn.commit()

# ---------------- LOAD DATA ---------------- #

df = pd.read_csv(
    "D:/StudentPerformanceDashboard/data/student_performance.csv"
)

# Remove extra spaces from columns

df.columns = df.columns.str.strip()

# ---------------- ADD ROLL NUMBER ---------------- #

df.insert(
    0,
    "Roll No",
    range(1, len(df) + 1)
)

# ---------------- NUMERIC SUBJECTS ---------------- #

numeric_subjects = (
    df.select_dtypes(include=np.number)
    .columns
    .tolist()
)

if "Roll No" in numeric_subjects:

    numeric_subjects.remove(
        "Roll No"
    )

# ---------------- SIDEBAR FILTERS ---------------- #

st.sidebar.header("📌 Filters")

# Student filter

student_filter = st.sidebar.multiselect(
    "Filter by Student(s)",
    df["Name"].unique()
)

# Subject filter

subject_filter = st.sidebar.multiselect(
    "Filter by Subject(s)",
    numeric_subjects
)

# ---------------- APPLY FILTERS ---------------- #

filtered_df = df.copy()

if student_filter:

    filtered_df = filtered_df[
        filtered_df["Name"].isin(
            student_filter
        )
    ]

if subject_filter:

    filtered_df = filtered_df[
        ["Roll No", "Name"]
        + subject_filter
    ]

# ---------------- FILTERED DATA ---------------- #

st.subheader("📋 Filtered Data")

st.dataframe(filtered_df)

# ---------------- SUBJECT-WISE AVERAGE ---------------- #

st.subheader(
    "📊 Subject-wise Average Marks"
)

avg_scores = (
    df[numeric_subjects]
    .mean()
    .sort_values(ascending=False)
)

fig, ax = plt.subplots(
    figsize=(10, 5)
)

sns.barplot(
    x=avg_scores.index,
    y=avg_scores.values,
    ax=ax,
    palette="Blues_d"
)

ax.set_ylabel("Average Marks")

ax.set_title(
    "Average Marks per Subject"
)

plt.xticks(rotation=45)

st.pyplot(fig)

# ---------------- ATTENDANCE OVERVIEW ---------------- #

if "Attendance (%)" in df.columns:

    st.subheader(
        "📅 Attendance Overview"
    )

    st.metric(
        "Average Attendance",
        f"{df['Attendance (%)'].mean():.2f}%"
    )

    st.line_chart(
        df["Attendance (%)"]
    )

# ---------------- SUMMARY STATISTICS ---------------- #

st.subheader(
    "📈 Summary Statistics"
)

st.dataframe(
    df[numeric_subjects].describe()
)

# ---------------- NORMALIZED SCORES ---------------- #

st.subheader(
    "⚙ Normalized Scores"
)

scaler = MinMaxScaler()

scaled_array = scaler.fit_transform(
    df[numeric_subjects]
)

scaled_df = pd.DataFrame(
    scaled_array * 100,
    columns=numeric_subjects
).round(2)

scaled_df.insert(
    0,
    "Roll No",
    df["Roll No"]
)

scaled_df.insert(
    1,
    "Name",
    df["Name"]
)

st.dataframe(scaled_df)

# ---------------- LEADERBOARD ---------------- #

st.subheader(
    "🏆 Leaderboard"
)

leaderboard = (
    df[
        [
            "Name",
            "Total Marks",
            "Average Score",
            "Performance Band"
        ]
    ]
    .sort_values(
        by="Total Marks",
        ascending=False
    )
    .reset_index(drop=True)
)

st.table(
    leaderboard.head(10)
)

# ---------------- GAMIFICATION BADGES ---------------- #

st.subheader(
    "🎖 Gamification Badges"
)

def assign_badge(row):

    if row["Average Score"] >= 90:
        return "Top Performer"

    elif row["Average Score"] >= 80:
        return "Consistent Achiever"

    elif row["Average Score"] >= 70:
        return "Needs Improvement"

    else:
        return "Needs Support"

df["Badge"] = df.apply(
    assign_badge,
    axis=1
)

st.dataframe(
    df[
        [
            "Name",
            "Average Score",
            "Performance Band",
            "Badge"
        ]
    ]
)

# ---------------- EXPORT FILTERED DATA ---------------- #

st.subheader(
    "⬇ Export Filtered Data"
)

# ---------------- CSV EXPORT ---------------- #

# ---------------- CSV EXPORT ---------------- #

csv = (
    filtered_df.to_csv(index=False)
    .encode("utf-8")
)

if st.download_button(
    label="Download as CSV",
    data=csv,
    file_name="filtered_data.csv",
    mime="text/csv"
):

    # ---------------- LOG CSV DOWNLOAD ---------------- #

    cursor.execute(
        """
        INSERT INTO admin_logs
        (admin_name, action)
        VALUES (?, ?)
        """,
        (
            "admin",
            "Downloaded CSV File"
        )
    )

    conn.commit()

    st.success(
        "CSV Downloaded Successfully!"
    )

# ---------------- EXCEL EXPORT ---------------- #

excel_buffer = io.BytesIO()

filtered_df.to_excel(
    excel_buffer,
    index=False,
    engine="openpyxl"
)

if st.download_button(
    label="Download as Excel",
    data=excel_buffer,
    file_name="filtered_data.xlsx",
    mime=(
        "application/vnd.openxmlformats-"
        "officedocument.spreadsheetml.sheet"
    )
):

    # ---------------- LOG EXCEL DOWNLOAD ---------------- #

    cursor.execute(
        """
        INSERT INTO admin_logs
        (admin_name, action)
        VALUES (?, ?)
        """,
        (
            "admin",
            "Downloaded Excel File"
        )
    )

    conn.commit()

    st.success(
        "Excel Downloaded Successfully!"
    )
# ---------------- LOGOUT BUTTON ---------------- #

st.divider()

if st.button("🚪 Logout"):

    # ---------------- LOG LOGOUT ---------------- #

    cursor.execute(
        """
        INSERT INTO admin_logs
        (admin_name, action)
        VALUES (?, ?)
        """,
        (
            "admin",
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