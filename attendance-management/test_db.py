import os
from database.db_manager import (
    add_student,
    fetch_all_students,
    fetch_attendance_by_date,
    init_db,
    mark_attendance,
)


def run_test():
    print("--- Starting Database Tests ---")

    # 1. Initialize DB tables
    init_db()
    print("✓ Database initialized successfully.")

    # 2. Test adding a new student
    success, msg = add_student("CS-101", "Ali Khan", "Computer Science")
    print(f"Add Student Result: {msg}")

    # 3. Test handling duplicate roll number
    dup_success, dup_msg = add_student("CS-101", "Another Student", "Physics")
    print(f"Duplicate Test Result: {dup_msg}")

    # 4. Fetch all students
    students = fetch_all_students()
    print(f"Current Students in DB: {students}")

    if students:
        student_id = students[0][0]  # Get ID of first student
        today_date = "2026-08-29"

        # 5. Mark Attendance
        mark_attendance(student_id, today_date, "Present")
        print(f"✓ Marked student ID {student_id} as Present for {today_date}.")

        # 6. Fetch Attendance by Date
        records = fetch_attendance_by_date(today_date)
        print(f"Attendance Records for {today_date}: {records}")

    print("--- Tests Completed Successfully ---")


if __name__ == "__main__":
    run_test()