from datetime import datetime


class AttendanceRecord:

  VALID_STATUSES = ["Present", "Absent", "Late"]

  def __init__(
      self, student_id: int, date: str, status: str, record_id: int = None
  ):
    self.id = record_id
    self.student_id = student_id
    self.date = date
    self.status = status.strip().title()

  def validate(self):
    """Validates attendance record parameters."""
    if self.status not in self.VALID_STATUSES:
      return (
          False,
          f"Invalid status! Must be one of {', '.join(self.VALID_STATUSES)}",
      )

    # Validate ISO date format (YYYY-MM-DD)
    try:
      datetime.strptime(self.date, "%Y-%m-%d")
    except ValueError:
      return False, "Date format must be YYYY-MM-DD!"

    return True, "Valid"

  def to_tuple(self):
    """Returns database-friendly tuple format."""
    return (self.student_id, self.date, self.status)

  def __repr__(self):
    return f"<Attendance Student:{self.student_id} | {self.date} : {self.status}>"