import sqlite3

# ---------------- DATABASE CONNECTION ---------------- #

conn = sqlite3.connect("database.db")

cursor = conn.cursor()

# ---------------- STUDENT LOGS TABLE ---------------- #

cursor.execute("""
CREATE TABLE IF NOT EXISTS student_logs (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    student_name TEXT,

    action TEXT,

    login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# ---------------- TEACHER LOGS TABLE ---------------- #

cursor.execute("""
CREATE TABLE IF NOT EXISTS teacher_logs (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    subject TEXT,

    action TEXT,

    login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# ---------------- ADMIN LOGS TABLE ---------------- #

cursor.execute("""
CREATE TABLE IF NOT EXISTS admin_logs (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    admin_name TEXT,

    action TEXT,

    login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# ---------------- SAVE CHANGES ---------------- #

conn.commit()

print("Database and tables created successfully!")