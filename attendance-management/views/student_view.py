import tkinter as tk
from tkinter import ttk, messagebox
from models.student import Student
from database import db_manager


class StudentView(ttk.Frame):

  def __init__(self, parent):
    super().__init__(parent)

    # Main split layout: Left = Form, Right = Data Table
    self._build_form_panel()
    self._build_table_panel()

    # Load initial student data from DB into table
    self.load_students()

  def _build_form_panel(self):
    """Creates input controls on the left panel."""
    form_frame = ttk.LabelFrame(self, text=" Add New Student ", padding=15)
    form_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

    # Roll Number Field
    ttk.Label(
        form_frame, text="Roll Number:", font=("Helvetica", 10, "bold")
    ).pack(anchor=tk.W, pady=(0, 2))
    self.roll_entry = ttk.Entry(form_frame, width=25)
    self.roll_entry.pack(anchor=tk.W, pady=(0, 10))

    # Student Name Field
    ttk.Label(
        form_frame, text="Full Name:", font=("Helvetica", 10, "bold")
    ).pack(anchor=tk.W, pady=(0, 2))
    self.name_entry = ttk.Entry(form_frame, width=25)
    self.name_entry.pack(anchor=tk.W, pady=(0, 10))

    # Department Field
    ttk.Label(
        form_frame, text="Department:", font=("Helvetica", 10, "bold")
    ).pack(anchor=tk.W, pady=(0, 2))
    self.dept_entry = ttk.Entry(form_frame, width=25)
    self.dept_entry.pack(anchor=tk.W, pady=(0, 15))

    # Add Student Button
    add_btn = ttk.Button(
        form_frame, text="➕ Save Student", command=self._handle_add_student
    )
    add_btn.pack(fill=tk.X, pady=5)

    # Clear Inputs Button
    clear_btn = ttk.Button(
        form_frame, text="🧹 Clear Fields", command=self._clear_fields
    )
    clear_btn.pack(fill=tk.X)

  def _build_table_panel(self):
    """Creates Treeview tabular grid on the right panel."""
    table_frame = ttk.LabelFrame(self, text=" Registered Students ", padding=10)
    table_frame.pack(
        side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10
    )

    # Define columns
    columns = ("id", "roll_no", "name", "department")
    self.tree = ttk.Treeview(
        table_frame, columns=columns, show="headings", selectmode="browse"
    )

    # Set Column Headings
    self.tree.heading("id", text="ID")
    self.tree.heading("roll_no", text="Roll No")
    self.tree.heading("name", text="Full Name")
    self.tree.heading("department", text="Department")

    # Set Column Column Widths & Alignments
    self.tree.column("id", width=40, anchor=tk.CENTER)
    self.tree.column("roll_no", width=100, anchor=tk.CENTER)
    self.tree.column("name", width=200, anchor=tk.W)
    self.tree.column("department", width=150, anchor=tk.W)

    # Vertical Scrollbar for table
    scrollbar = ttk.Scrollbar(
        table_frame, orient=tk.VERTICAL, command=self.tree.yview
    )
    self.tree.configure(yscrollcommand=scrollbar.set)

    # Pack grid & scrollbar
    self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

  def _handle_add_student(self):
    """Retrieves form inputs, validates using Model, and saves to DB."""
    roll = self.roll_entry.get()
    name = self.name_entry.get()
    dept = self.dept_entry.get()

    # Instantiate Student model object
    student = Student(roll_no=roll, name=name, department=dept)

    # Validate using model logic
    is_valid, error_msg = student.validate()
    if not is_valid:
      messagebox.showwarning("Validation Warning", error_msg)
      return

    # Persist data using db_manager layer
    success, db_msg = db_manager.add_student(
        student.roll_no, student.name, student.department
    )

    if success:
      messagebox.showinfo("Success", db_msg)
      self._clear_fields()
      self.load_students()
    else:
      messagebox.showerror("Database Error", db_msg)

  def load_students(self):
    """Clears existing items in Treeview and reloads data from SQLite."""
    # Remove existing items in table
    for item in self.tree.get_children():
      self.tree.delete(item)

    # Fetch fresh rows from database
    records = db_manager.fetch_all_students()

    # Populate rows into table
    for record in records:
      self.tree.insert("", tk.END, values=record)

  def _clear_fields(self):
    """Clears text input fields."""
    self.roll_entry.delete(0, tk.END)
    self.name_entry.delete(0, tk.END)
    self.dept_entry.delete(0, tk.END)