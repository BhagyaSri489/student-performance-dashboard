import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
st.set_page_config(page_title="Instructor Dashboard", layout="wide")
st.title("Instructor Dashboard")
# Access Control
if "registered" not in st.session_state or not st.session_state.registered or st.session_state.role != "Instructor":
    st.error("Access Denied. Please register/login as Instructor from the main app.")
    st.stop()
# Load dataset
df = pd.read_csv("data/student_performance.csv")
df.insert(0, "Roll No", range(1, len(df) + 1))
numeric_subjects = df.select_dtypes(include=np.number).columns.tolist()
if "Roll No" in numeric_subjects:
    numeric_subjects.remove("Roll No")
# Subject search
subject_name = st.text_input("Enter your subject name to view marks").strip()
if subject_name:
    if subject_name in numeric_subjects:
        st.subheader(f"Marks for {subject_name}")
        subject_marks = df[["Roll No", "Name", subject_name]].reset_index(drop=True)
        st.dataframe(subject_marks)
        # Histogram
        st.subheader(f"Distribution of {subject_name} Marks")
        fig1, ax1 = plt.subplots(figsize=(8, 4))
        sns.histplot(df[subject_name], bins=10, kde=True, color="skyblue", ax=ax1)
        ax1.set_xlabel("Marks")
        ax1.set_ylabel("Number of Students")
        ax1.set_title(f"{subject_name} Marks Distribution")
        st.pyplot(fig1)
        # Boxplot
        st.subheader(f"Boxplot for {subject_name}")
        fig2, ax2 = plt.subplots(figsize=(6, 4))
        sns.boxplot(y=df[subject_name], color="lightgreen", ax=ax2)
        ax2.set_title(f"{subject_name} Score Spread")
        st.pyplot(fig2)
        # Top 10 Students
        st.subheader(f"Top 10 Students in {subject_name}")
        top_students = df.sort_values(by=subject_name, ascending=False)[["Roll No", "Name", subject_name]].head(10).reset_index(drop=True)
        fig3, ax3 = plt.subplots(figsize=(10, 6))
        bars = ax3.barh(
            top_students["Name"],
            top_students[subject_name],
            color=plt.cm.viridis(top_students[subject_name] / top_students[subject_name].max())
        )
        ax3.invert_yaxis()
        ax3.set_xlabel("Marks")
        ax3.set_title(f"Top 10 Performers in {subject_name}")
        for i, bar in enumerate(bars):
            ax3.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
                     f"{top_students[subject_name][i]:.1f}", va='center')
        st.pyplot(fig3)
        # Download chart
        st.subheader("Download Top 10 Chart")
        chart_path = f"charts/top10_{subject_name}.png"
        os.makedirs("charts", exist_ok=True)
        fig3.savefig(chart_path, bbox_inches="tight")
        with open(chart_path, "rb") as file:
            st.download_button(
                label="Download Chart",
                data=file,
                file_name=f"top10_{subject_name}.png",
                mime="image/png"
            )
    else:
        st.error("Subject not found. Please check the name.")
else:
    st.info("Enter a subject name to view marks.")

