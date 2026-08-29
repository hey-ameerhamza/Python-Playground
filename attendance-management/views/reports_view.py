import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import tkinter as tk
from tkinter import ttk, messagebox
from database import db_manager


class ReportsView(ttk.Frame):

  def __init__(self, parent):
    super().__init__(parent)

    self._build_top_bar()
    self._build_table_panel()
    self.load_report_data()

  def _build_top_bar(self):
    """Header bar with refresh controls."""
    top_frame = ttk.LabelFrame(self, text=" Analytics Summary ", padding=10)
    top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=(10, 5))

    refresh_btn = ttk.Button(
        top_frame,
        text="🔄 Refresh Summary Report",
        command=self.load_report_data,
    )
    refresh_btn.pack(side=tk.LEFT)

    info_label = ttk.Label(
        top_frame,
        text="⚠️ Rows highlighted in red drop below 75% threshold",
        font=("Helvetica", 9, "italic"),
        foreground="#DC2626",
    )
    info_label.pack(side=tk.RIGHT, padx=10)

  def _build_table_panel(self):
    """Grid displaying student attendance percentages."""
    table_frame = ttk.LabelFrame(
        self, text=" Attendance Summary ", padding=10
    )
    table_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=5)

    columns = (
        "roll_no",
        "name",
        "department",
        "total_sessions",
        "present_count",
        "percentage",
        "status_flag",
    )
    self.tree = ttk.Treeview(
        table_frame, columns=columns, show="headings", selectmode="browse"
    )

    # Column Headings
    self.tree.heading("roll_no", text="Roll No")
    self.tree.heading("name", text="Student Name")
    self.tree.heading("department", text="Department")
    self.tree.heading("total_sessions", text="Total Sessions")
    self.tree.heading("present_count", text="Present Days")
    self.tree.heading("percentage", text="Attendance %")
    self.tree.heading("status_flag", text="Status")

    # Column Formatting
    self.tree.column("roll_no", width=100, anchor=tk.CENTER)
    self.tree.column("name", width=180, anchor=tk.W)
    self.tree.column("department", width=120, anchor=tk.W)
    self.tree.column("total_sessions", width=100, anchor=tk.CENTER)
    self.tree.column("present_count", width=100, anchor=tk.CENTER)
    self.tree.column("percentage", width=100, anchor=tk.CENTER)
    self.tree.column("status_flag", width=120, anchor=tk.CENTER)

    # Configure Color Tags for Alert Highlighting
    self.tree.tag_configure(
        "low_attendance", background="#FEE2E2", foreground="#991B1B"
    )
    self.tree.tag_configure("good_attendance", background="#DCFCE7")

    scrollbar = ttk.Scrollbar(
        table_frame, orient=tk.VERTICAL, command=self.tree.yview
    )
    self.tree.configure(yscrollcommand=scrollbar.set)

    self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

  def load_report_data(self):
    """Calculates attendance percentages and renders rows with visual indicators."""
    for item in self.tree.get_children():
      self.tree.delete(item)

    records = db_manager.fetch_attendance_summary()

    for rec in records:
      student_id, roll_no, name, dept, total_sessions, present_count = rec

      # Avoid Division by Zero if no classes recorded yet
      if total_sessions == 0 or present_count is None:
        percentage = 0.0
        present_count = 0
      else:
        percentage = round((present_count / total_sessions) * 100, 2)

      # Determine status flag & formatting tag
      if percentage >= 75.0:
        status_flag = "Eligible"
        tag = "good_attendance"
      else:
        status_flag = "Low Attendance"
        tag = "low_attendance"

      row_values = (
          roll_no,
          name,
          dept,
          total_sessions,
          present_count,
          f"{percentage}%",
          status_flag,
      )
      self.tree.insert("", tk.END, values=row_values, tags=(tag,))