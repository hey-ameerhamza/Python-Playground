import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "attendance.db")


def get_connection():
    """Establishes and returns a database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db():
    """Creates tables if they do not exist."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            roll_no TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            department TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
            UNIQUE(student_id, date)
        )
    """)

    conn.commit()
    conn.close()


def add_student(roll_no, name, department):
    """Inserts a new student into the students table."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO students (roll_no, name, department) VALUES (?, ?, ?)",
            (roll_no, name, department),
        )
        conn.commit()
        return True, "Student added successfully!"
    except sqlite3.IntegrityError:
        return False, "Error: Roll Number already exists!"
    finally:
        conn.close()


def fetch_all_students():
    """Retrieves all registered students."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, roll_no, name, department FROM students")
    records = cursor.fetchall()
    conn.close()
    return records


def mark_attendance(student_id, date_str, status):
    """Inserts or updates daily attendance for a specific student."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO attendance (student_id, date, status)
        VALUES (?, ?, ?)
        ON CONFLICT(student_id, date) DO UPDATE SET status = excluded.status
    """,
        (student_id, date_str, status),
    )
    conn.commit()
    conn.close()


def fetch_attendance_by_date(date_str):
    """Retrieves attendance records for a specific date."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT s.id, s.roll_no, s.name, COALESCE(a.status, 'Absent') as status
        FROM students s
        LEFT JOIN attendance a ON s.id = a.student_id AND a.date = ?
    """,
        (date_str,),
    )
    records = cursor.fetchall()
    conn.close()
    return records

def fetch_attendance_summary():
  """Calculates total classes, total present, and percentage for every student."""
  conn = get_connection()
  cursor = conn.cursor()
  cursor.execute("""
        SELECT 
            s.id,
            s.roll_no,
            s.name,
            s.department,
            COUNT(a.id) AS total_sessions,
            SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) AS present_count
        FROM students s
        LEFT JOIN attendance a ON s.id = a.student_id
        GROUP BY s.id
    """)
  records = cursor.fetchall()
  conn.close()
  return records