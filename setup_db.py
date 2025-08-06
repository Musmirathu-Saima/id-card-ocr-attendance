import sqlite3

# Connect to (or create) database
conn = sqlite3.connect("students.db")
cursor = conn.cursor()

# Create students table
cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    usn TEXT,
    branch TEXT,
    id_no TEXT,
    marked_present INTEGER DEFAULT 0
)
""")

# Insert a sample student (this should match the ID card text you’ll scan)
cursor.execute("""
INSERT INTO students (name, usn, branch, id_no)
VALUES (?, ?, ?, ?)
""", ("MUSMIRATHU SAIMA N", "1RG22CS052", "CSE", "1517"))

conn.commit()
conn.close()

print("✅ Database and sample student created successfully.")
