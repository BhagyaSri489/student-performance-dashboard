import sqlite3
import sys

role = sys.argv[1] if len(sys.argv) > 1 else "all"

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

if role == "student":
    cursor.execute("DELETE FROM student_logs")

elif role == "teacher":
    cursor.execute("DELETE FROM teacher_logs")

elif role == "admin":
    cursor.execute("DELETE FROM admin_logs")

elif role == "all":
    cursor.execute("DELETE FROM student_logs")
    cursor.execute("DELETE FROM teacher_logs")
    cursor.execute("DELETE FROM admin_logs")

conn.commit()
conn.close()

print(f"{role} logs deleted successfully!")