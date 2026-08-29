import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import tkinter as tk
from tkinter import ttk
from views.attendance_view import AttendanceView
from views.reports_view import ReportsView  # <--- Import ReportsView
from views.student_view import StudentView


class MainWindow(tk.Tk):

  def __init__(self):
    super().__init__()

    self.title("Attendance Management System (by Hamza)")
    self.geometry("950x650")
    self.minsize(850, 550)

    self._setup_styles()
    self._build_header()
    self._build_tabs()

  def _setup_styles(self):
    self.style = ttk.Style(self)
    self.style.theme_use("clam")
    self.style.configure(
        "TNotebook.Tab", font=("Helvetica", 11, "bold"), padding=[12, 6]
    )
    self.style.configure(
        "Header.TLabel",
        font=("Helvetica", 18, "bold"),
        background="#1E293B",
        foreground="#FFFFFF",
    )

  def _build_header(self):
    header_frame = tk.Frame(self, bg="#1E293B", height=60)
    header_frame.pack(side=tk.TOP, fill=tk.X)
    header_frame.pack_propagate(False)

    title_label = ttk.Label(
        header_frame,
        text="🎓 Attendance Management System (by Hamza)",
        style="Header.TLabel",
    )
    title_label.pack(side=tk.LEFT, padx=20, pady=12)

  def _build_tabs(self):
    self.notebook = ttk.Notebook(self)
    self.notebook.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Instantiate Views
    self.student_tab = StudentView(self.notebook)
    self.attendance_tab = AttendanceView(self.notebook)
    self.reports_tab = ReportsView(self.notebook)  # <--- Instantiate ReportsView

    # Add Tabs
    self.notebook.add(self.student_tab, text=" 👨‍🎓 Student Management ")
    self.notebook.add(self.attendance_tab, text=" 📅 Mark Attendance ")
    self.notebook.add(
        self.reports_tab, text=" 📊 Summary & Reports "
    )  # <--- Add 3rd Tab


if __name__ == "__main__":
  app = MainWindow()
  app.mainloop()