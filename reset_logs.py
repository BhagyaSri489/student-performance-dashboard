import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("DELETE FROM student_logs")
cursor.execute("DELETE FROM teacher_logs")
cursor.execute("DELETE FROM admin_logs")

conn.commit()
conn.close()

print("All logs cleared. Fresh logging started.")