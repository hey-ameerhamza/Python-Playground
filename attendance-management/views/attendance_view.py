import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime
import tkinter as tk
from tkinter import messagebox, ttk

from database import db_manager
from models.attendance import AttendanceRecord


class AttendanceView(ttk.Frame):

  def __init__(self, parent):
    super().__init__(parent)

    self.attendance_vars = {}

    # Build View Panels
    self._build_header_panel()
    self._build_table_panel()
    self._build_action_panel()

    # Load today's date attendance by default
    self.load_attendance_for_date()

  def _build_header_panel(self):
    """Top bar for selecting attendance date."""
    header_frame = ttk.LabelFrame(self, text=" Select Date ", padding=10)
    header_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=(10, 5))

    ttk.Label(
        header_frame, text="Date (YYYY-MM-DD):", font=("Helvetica", 10, "bold")
    ).pack(side=tk.LEFT, padx=(0, 5))

    today_str = datetime.now().strftime("%Y-%m-%d")
    self.date_entry = ttk.Entry(header_frame, width=15)
    self.date_entry.insert(0, today_str)
    self.date_entry.pack(side=tk.LEFT, padx=(0, 10))

    load_btn = ttk.Button(
        header_frame, text="🔍 Fetch Records", command=self.load_attendance_for_date
    )
    load_btn.pack(side=tk.LEFT)

  def _build_table_panel(self):
    """Grid displaying students with interactive checkbuttons."""
    table_frame = ttk.LabelFrame(self, text=" Student Roll ", padding=10)
    table_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=5)

    columns = ("student_id", "roll_no", "name", "status")
    self.tree = ttk.Treeview(
        table_frame, columns=columns, show="headings", selectmode="browse"
    )

    self.tree.heading("student_id", text="ID")
    self.tree.heading("roll_no", text="Roll No")
    self.tree.heading("name", text="Student Name")
    self.tree.heading("status", text="Attendance Status")

    self.tree.column("student_id", width=40, anchor=tk.CENTER)
    self.tree.column("roll_no", width=120, anchor=tk.CENTER)
    self.tree.column("name", width=250, anchor=tk.W)
    self.tree.column("status", width=150, anchor=tk.CENTER)

    # Configure Color Tags
    self.tree.tag_configure(
        "present_row", background="#DCFCE7", foreground="#166534"
    )
    self.tree.tag_configure(
        "absent_row", background="#FEE2E2", foreground="#991B1B"
    )

    scrollbar = ttk.Scrollbar(
        table_frame, orient=tk.VERTICAL, command=self.tree.yview
    )
    self.tree.configure(yscrollcommand=scrollbar.set)

    self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Bind double click event
    self.tree.bind("<Double-1>", self._toggle_status)

  def _build_action_panel(self):
    """Bottom button container for bulk and individual operations."""
    action_frame = tk.Frame(self)
    action_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=(5, 10))

    # Single Student Toggle Button
    toggle_btn = ttk.Button(
        action_frame,
        text="🔄 Toggle Selected Status",
        command=self._toggle_selected_student,
    )
    toggle_btn.pack(side=tk.LEFT, padx=(0, 10))

    # Bulk Action Buttons
    mark_all_btn = ttk.Button(
        action_frame, text="✅ Mark All Present", command=self._mark_all_present
    )
    mark_all_btn.pack(side=tk.LEFT, padx=(0, 5))

    unmark_all_btn = ttk.Button(
        action_frame, text="❌ Mark All Absent", command=self._mark_all_absent
    )
    unmark_all_btn.pack(side=tk.LEFT, padx=(0, 10))

    save_btn = ttk.Button(
        action_frame, text="💾 Save Attendance", command=self._save_attendance
    )
    save_btn.pack(side=tk.RIGHT)

  def load_attendance_for_date(self):
    """Fetches attendance records for the entered date and populates Treeview."""
    date_str = self.date_entry.get().strip()

    temp_record = AttendanceRecord(
        student_id=0, date=date_str, status="Present"
    )
    is_valid, err_msg = temp_record.validate()
    if not is_valid:
      messagebox.showerror("Invalid Date", err_msg)
      return

    for item in self.tree.get_children():
      self.tree.delete(item)

    self.attendance_vars.clear()

    records = db_manager.fetch_attendance_by_date(date_str)

    if not records:
      messagebox.showinfo("Info", "No registered students found!")
      return

    for rec in records:
      student_id, roll_no, name, status = rec
      tag = "present_row" if status == "Present" else "absent_row"

      item_id = self.tree.insert(
          "", tk.END, values=(student_id, roll_no, name, status), tags=(tag,)
      )
      self.attendance_vars[item_id] = status

  def _toggle_selected_student(self):
    """Toggles status for the currently selected student row."""
    selected_item = self.tree.selection()
    if not selected_item:
      messagebox.showwarning(
          "Selection Warning", "Please select a student from the table first!"
      )
      return

    self._toggle_status(event=None)

  def _toggle_status(self, event=None):
    """Toggles status between Present and Absent when double-clicking or pressing button."""
    selected_item = self.tree.selection()
    if not selected_item:
      return

    item_id = selected_item[0]
    current_values = list(self.tree.item(item_id, "values"))
    current_status = current_values[3]

    new_status = "Absent" if current_status == "Present" else "Present"
    new_tag = "present_row" if new_status == "Present" else "absent_row"

    current_values[3] = new_status

    self.tree.item(item_id, values=current_values, tags=(new_tag,))
    self.attendance_vars[item_id] = new_status

  def _mark_all_present(self):
    """Sets status of all currently displayed students to Present."""
    for item_id in self.tree.get_children():
      values = list(self.tree.item(item_id, "values"))
      values[3] = "Present"
      self.tree.item(item_id, values=values, tags=("present_row",))
      self.attendance_vars[item_id] = "Present"

  def _mark_all_absent(self):
    """Sets status of all currently displayed students to Absent."""
    for item_id in self.tree.get_children():
      values = list(self.tree.item(item_id, "values"))
      values[3] = "Absent"
      self.tree.item(item_id, values=values, tags=("absent_row",))
      self.attendance_vars[item_id] = "Absent"

  def _save_attendance(self):
    """Persists all attendance updates to SQLite database."""
    date_str = self.date_entry.get().strip()

    count = 0
    for item_id in self.tree.get_children():
      values = self.tree.item(item_id, "values")
      student_id = int(values[0])
      status = values[3]

      record = AttendanceRecord(
          student_id=student_id, date=date_str, status=status
      )
      is_valid, err_msg = record.validate()

      if is_valid:
        db_manager.mark_attendance(
            record.student_id, record.date, record.status
        )
        count += 1
      else:
        messagebox.showwarning(
            "Validation Error", f"Student ID {student_id}: {err_msg}"
        )
        return

    messagebox.showinfo(
        "Saved", f"Successfully saved attendance for {count} student(s)!"
    )