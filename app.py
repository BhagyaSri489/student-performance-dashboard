import streamlit as st
import pandas as pd


# ---------------- PAGE CONFIG ---------------- #

st.set_page_config(
    page_title="Student Performance Dashboard",
    layout="wide"
)

st.title("📊 Student Performance Dashboard")

# ---------------- LOAD CSV ---------------- #

df = pd.read_csv(
    "D:/StudentPerformanceDashboard/data/student_performance.csv"
)

# Remove extra spaces from columns

df.columns = df.columns.str.strip()

# ---------------- CREATE STUDENT CREDENTIALS ---------------- #

student_credentials = {}

for index, row in df.iterrows():

    # Student username

    username = str(
        row["Name"]
    ).strip()

    # Remove spaces

    clean_name = username.replace(
        " ",
        ""
    )

    # Count letters

    letter_count = len(clean_name)

    # Password format

    password = (
        clean_name
        + str(letter_count)
    )

    # Store credentials

    student_credentials[
        username
    ] = password

# ---------------- SESSION STATE ---------------- #

if "page" not in st.session_state:

    st.session_state.page = "home"

if "role" not in st.session_state:

    st.session_state.role = None

if "logged_in" not in st.session_state:

    st.session_state.logged_in = False

if "username" not in st.session_state:

    st.session_state.username = None

# ---------------- LOGIN CREDENTIALS ---------------- #

credentials = {

    "Admin": {

        "admin": "admin123"
    },

    "Instructor": {

        "english": "eng123",

        "math": "math123",

        "science": "sci123"
    },

    "Student": student_credentials
}

# ---------------- HOME PAGE ---------------- #

if st.session_state.page == "home":

    st.subheader(
        "Welcome to Student Performance Dashboard"
    )

    st.write(
        "Choose your role:"
    )

    col1, col2, col3 = st.columns(3)

    # ---------------- ADMIN ---------------- #

    with col1:

        if st.button("🛠 Admin"):

            st.session_state.role = "Admin"

            st.session_state.page = "login"

            st.rerun()

    # ---------------- INSTRUCTOR ---------------- #

    with col2:

        if st.button("📘 Instructor"):

            st.session_state.role = "Instructor"

            st.session_state.page = "login"

            st.rerun()

    # ---------------- STUDENT ---------------- #

    with col3:

        if st.button("🎓 Student"):

            st.session_state.role = "Student"

            st.session_state.page = "login"

            st.rerun()

# ---------------- LOGIN PAGE ---------------- #

elif st.session_state.page == "login":

    st.subheader(
        f"{st.session_state.role} Login"
    )

    username = st.text_input(
        "Enter Username"
    )

    password = st.text_input(
        "Enter Password",
        type="password"
    )

    # ---------------- LOGIN BUTTON ---------------- #

    if st.button("Login"):

        role = (
            st.session_state.role
        )

        # ---------------- VALIDATION ---------------- #

        if (
            username in credentials[role]
            and
            credentials[role][username]
            == password
        ):

            # ---------------- LOGIN SUCCESS ---------------- #

            st.success(
                "✅ Login Successful!"
            )

            st.session_state.logged_in = True

            st.session_state.username = username

            # ---------------- PAGE REDIRECTION ---------------- #

            if role == "Admin":

                st.switch_page(
                    "pages/admin.py"
                )

            elif role == "Instructor":

                st.switch_page(
                    "pages/instructor.py"
                )

            elif role == "Student":

                st.switch_page(
                    "pages/student.py"
                )

        # ---------------- INVALID LOGIN ---------------- #

        else:

            st.error(
                "❌ Invalid Username or Password"
            )

    # ---------------- BACK BUTTON ---------------- #

    if st.button("⬅ Back to Home"):

        st.session_state.page = "home"

        st.rerun()