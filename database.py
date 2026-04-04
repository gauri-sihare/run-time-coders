import sqlite3

conn = sqlite3.connect("posture.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    total_time TEXT,
    good_time TEXT,
    bad_time TEXT
)
""")

def save_record(date, total, good, bad):
    cursor.execute("INSERT INTO records (date, total_time, good_time, bad_time) VALUES (?, ?, ?, ?)",
                   (date, total, good, bad))
    conn.commit()