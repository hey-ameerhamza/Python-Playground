class Student:

  def __init__(
      self, roll_no: str, name: str, department: str, student_id: int = None
  ):
    self.id = student_id
    self.roll_no = roll_no.strip().upper()
    self.name = name.strip().title()
    self.department = department.strip()

  def validate(self):
    """Validates student data before saving to DB."""
    if not self.roll_no:
      return False, "Roll number cannot be empty!"
    if not self.name:
      return False, "Student name cannot be empty!"
    if not self.department:
      return False, "Department cannot be empty!"
    return True, "Valid"

  def to_tuple(self):
    """Returns database-friendly tuple format."""
    return (self.roll_no, self.name, self.department)

  def __repr__(self):
    return f"<Student {self.roll_no} - {self.name}>"