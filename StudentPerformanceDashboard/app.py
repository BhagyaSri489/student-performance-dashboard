import streamlit as st

st.set_page_config(page_title="Student Performance Dashboard", layout="wide")
st.title("📊 Student Performance Dashboard")

# Session state initialization
if "registered" not in st.session_state:
    st.session_state.registered = False
if "role" not in st.session_state:
    st.session_state.role = None

# Login form
if not st.session_state.registered:
    st.subheader("Register / Login to Continue")
    username = st.text_input("👤 Enter Username")
    password = st.text_input("🔑 Enter Password", type="password")

    if st.button("✅ Submit"):
        if username and password:
            st.session_state.registered = True
            st.success(f"Welcome, {username}! You are now logged in.")
        else:
            st.error("Please enter both username and password.")
else:
    st.success("✅ Logged in successfully")
    st.markdown("### Choose your role to continue:")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🛠 Admin"):
            st.session_state.role = "Admin"
            st.switch_page("pages/admin.py")
    with col2:
        if st.button("📘 Instructor"):
            st.session_state.role = "Instructor"
            st.switch_page("pages/instructor.py")
    with col3:
        if st.button("🎓 Student"):
            st.session_state.role = "Student"
            st.switch_page("pages/student.py")

    if st.button("🚪 Logout"):
        st.session_state.registered = False
        st.session_state.role = None
        st.info("You have logged out.")
