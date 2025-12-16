import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
import re

DB_PATH = "employees.db"

# --- Validation helpers ---
def is_valid_employee_id(employee_id: str) -> bool:
    return re.match(r"^[A-Za-z0-9_-]{3,20}$", employee_id) is not None

def is_valid_email(email: str) -> bool:
    return re.match(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$", email) is not None

def is_valid_salary(value: str) -> bool:
    try:
        return float(value) >= 0
    except ValueError:
        return False

# --- Database setup ---
def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS employees (
        employee_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        department TEXT,
        salary REAL NOT NULL CHECK (salary >= 0)
    );
    """)
    conn.commit()
    conn.close()

def add_employee(employee_id, name, email, department, salary):
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("INSERT INTO employees VALUES (?, ?, ?, ?, ?)",
                     (employee_id, name, email, department, salary))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError as e:
        messagebox.showerror("Error", f"Database error: {e}")
        return False

def get_all_employees():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute("SELECT * FROM employees")
    rows = cur.fetchall()
    conn.close()
    return rows

def update_employee(employee_id, name, email, department, salary):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute("""
        UPDATE employees
        SET name=?, email=?, department=?, salary=?
        WHERE employee_id=?
    """, (name, email, department, salary, employee_id))
    conn.commit()
    conn.close()
    return cur.rowcount

def delete_employee(employee_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute("DELETE FROM employees WHERE employee_id=?", (employee_id,))
    conn.commit()
    conn.close()
    return cur.rowcount

# --- GUI Application ---
class EmployeeApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Employee Management System")

        # Form fields
        self.id_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.dept_var = tk.StringVar()
        self.salary_var = tk.StringVar()

        form_frame = tk.Frame(self.root)
        form_frame.pack(pady=10)

        tk.Label(form_frame, text="Employee ID").grid(row=0, column=0)
        tk.Entry(form_frame, textvariable=self.id_var).grid(row=0, column=1)

        tk.Label(form_frame, text="Name").grid(row=1, column=0)
        tk.Entry(form_frame, textvariable=self.name_var).grid(row=1, column=1)

        tk.Label(form_frame, text="Email").grid(row=2, column=0)
        tk.Entry(form_frame, textvariable=self.email_var).grid(row=2, column=1)

        tk.Label(form_frame, text="Department").grid(row=3, column=0)
        tk.Entry(form_frame, textvariable=self.dept_var).grid(row=3, column=1)

        tk.Label(form_frame, text="Salary").grid(row=4, column=0)
        tk.Entry(form_frame, textvariable=self.salary_var).grid(row=4, column=1)

        # Buttons
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Add", command=self.add).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Update", command=self.update).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Delete", command=self.delete).grid(row=0, column=2, padx=5)
        tk.Button(btn_frame, text="Refresh", command=self.refresh).grid(row=0, column=3, padx=5)

        # Table
        self.tree = ttk.Treeview(self.root, columns=("ID", "Name", "Email", "Dept", "Salary"), show="headings")
        for col in ("ID", "Name", "Email", "Dept", "Salary"):
            self.tree.heading(col, text=col)
        self.tree.pack(fill="both", expand=True)

        self.refresh()

    def add(self):
        eid, name, email, dept, salary = self.id_var.get(), self.name_var.get(), self.email_var.get(), self.dept_var.get(), self.salary_var.get()
        if not is_valid_employee_id(eid):
            messagebox.showerror("Error", "Invalid Employee ID")
            return
        if not is_valid_email(email):
            messagebox.showerror("Error", "Invalid Email")
            return
        if not is_valid_salary(salary):
            messagebox.showerror("Error", "Invalid Salary")
            return
        if add_employee(eid, name, email, dept, float(salary)):
            messagebox.showinfo("Success", "Employee added")
            self.refresh()

    def update(self):
        eid, name, email, dept, salary = self.id_var.get(), self.name_var.get(), self.email_var.get(), self.dept_var.get(), self.salary_var.get()
        if update_employee(eid, name, email, dept, float(salary)):
            messagebox.showinfo("Success", "Employee updated")
            self.refresh()
        else:
            messagebox.showerror("Error", "Employee not found")

    def delete(self):
        eid = self.id_var.get()
        if delete_employee(eid):
            messagebox.showinfo("Success", "Employee deleted")
            self.refresh()
        else:
            messagebox.showerror("Error", "Employee not found")

    def refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for row in get_all_employees():
            self.tree.insert("", "end", values=row)

# --- Run the app ---
if __name__ == "__main__":
    init_db() 
    app = EmployeeApp()
