import mysql.connector
from tkinter import *
from tkinter import messagebox
import csv
from datetime import datetime
import os

# MySQL Database Connection
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="piyush")

cursor = conn.cursor()
cursor.execute("CREATE DATABASE IF NOT EXISTS employee_attendance")
cursor.execute("USE employee_attendance")
cursor.execute("CREATE TABLE IF NOT EXISTS Users (user_id INT AUTO_INCREMENT PRIMARY KEY,username VARCHAR(50) UNIQUE,password VARCHAR(255),role ENUM('admin', 'user') NOT NULL)")
cursor.execute("CREATE TABLE IF NOT EXISTS Employees (emp_id INT PRIMARY KEY,name VARCHAR(100),department VARCHAR(100))")
cursor.execute("CREATE TABLE IF NOT EXISTS Attendance (attendance_id INT AUTO_INCREMENT PRIMARY KEY,emp_id INT,date DATE,status BOOLEAN,FOREIGN KEY (emp_id) REFERENCES Employees(emp_id))")



# --- Helper Functions ---

# Function to add a new user
def add_user(username, password, role):
    try:
        cursor.execute("INSERT INTO Users (username, password, role) VALUES (%s, %s, %s)", (username, password, role))
        conn.commit()
        messagebox.showinfo("Success", f"User '{username}' added successfully!")
    except mysql.connector.IntegrityError:
        messagebox.showerror("Error", "Username already exists.")

# Function to add a new employee
def add_employee(emp_id, name, department):
    cursor.execute("INSERT INTO Employees (emp_id, name, department) VALUES (%s, %s, %s)", (emp_id, name, department))
    conn.commit()
    messagebox.showinfo("Success", "Employee added successfully!")

# Function to delete an employee
def delete_employee(emp_id):
    cursor.execute("DELETE FROM Employees WHERE emp_id = " +emp_id)
    conn.commit()
    messagebox.showinfo("Success", "Employee deleted successfully!")

# Function to mark attendance
def mark_attendance(emp_id, status):
    today = datetime.today().date()
    cursor.execute("INSERT INTO Attendance (emp_id, date, status) VALUES (%s, %s, %s)", (emp_id, today, status))
    conn.commit()

# Function to export attendance to CSV
def export_attendance(month):
    cursor.execute("SELECT Employees.name, Attendance.date, Attendance.status FROM Attendance JOIN Employees ON Attendance.emp_id = Employees.emp_id WHERE MONTH(date) = %s", (month,))
    rows = cursor.fetchall()

    with open('attendance_report.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Employee Name", "Date", "Status"])
        for row in rows:
            writer.writerow([row[0], row[1], "Present" if row[2] else "Absent"])

    messagebox.showinfo("Success", "Attendance exported to 'attendance_report.csv'.")
    os.startfile("D://Internship/attendance_report.csv")


# --- GUI Components ---

# Function to open main menu after login
def open_main_menu(username, role):
    main_menu = Tk()
    main_menu.title("Employee Attendance System")
    main_menu.geometry("400x400")

    if role == "admin":
        Button(main_menu, text="Add Employee", command=open_add_employee_window).pack(pady=5)
        Button(main_menu, text="Delete Employee", command=open_delete_employee_window).pack(pady=5)
    Button(main_menu, text="Mark Attendance", command=open_mark_attendance_window).pack(pady=5)
    Button(main_menu, text="Export Attendance", command=open_export_attendance_window).pack(pady=5)
    Button(main_menu, text="Logout", command=main_menu.destroy).pack(pady=5)

# Function to open the "Add Employee" window
def open_add_employee_window():
    add_employee_window = Tk()
    add_employee_window.title("Add Employee")

    Label(add_employee_window, text="Employee ID").pack()
    emp_id_entry = Entry(add_employee_window)
    emp_id_entry.pack()

    Label(add_employee_window, text="Name").pack()
    name_entry = Entry(add_employee_window)
    name_entry.pack()

    Label(add_employee_window, text="Department").pack()
    department_entry = Entry(add_employee_window)
    department_entry.pack()

    Button(add_employee_window, text="Add", command=lambda: add_employee(
        emp_id_entry.get(), name_entry.get(), department_entry.get())).pack()

# Function to open the "Delete Employee" window
def open_delete_employee_window():
    delete_employee_window = Tk()
    delete_employee_window.title("Delete Employee")

    Label(delete_employee_window, text="Employee ID").pack()
    emp_id_entry = Entry(delete_employee_window)
    emp_id_entry.pack()

    Button(delete_employee_window, text="Delete", command=lambda: delete_employee(
        emp_id_entry.get())).pack()

# Function to open the "Mark Attendance" window
def open_mark_attendance_window():
    mark_attendance_window = Tk()
    mark_attendance_window.title("Mark Attendance")

    Label(mark_attendance_window, text="Mark Attendance").pack()

    cursor.execute("SELECT emp_id, name FROM Employees")
    employees = cursor.fetchall()

    check_vars = []
    for emp in employees:
        check_var = IntVar()
        check_vars.append((emp[0], check_var))
        Checkbutton(mark_attendance_window, text=emp[1], variable=check_var).pack()

    Button(mark_attendance_window, text="Submit", command=lambda: mark_all_attendance(check_vars)).pack()

# Function to mark attendance based on ticked checkboxes
def mark_all_attendance(check_vars):
    for emp_id, check_var in check_vars:
        status = check_var.get() == 1  # 1 if checked (Present), 0 if unchecked (Absent)
        mark_attendance(emp_id, status)
    messagebox.showinfo("Success", "Attendance marked successfully!")

# Function to open the "Export Attendance" window
def open_export_attendance_window():
    export_attendance_window = Tk()
    export_attendance_window.title("Export Attendance")

    Label(export_attendance_window, text="Month (1-12)").pack()
    month_entry = Entry(export_attendance_window)
    month_entry.pack()

    Button(export_attendance_window, text="Export", command=lambda: export_attendance(
        month_entry.get())).pack()

# Function to handle login
def login():
    username = username_entry.get()
    password = password_entry.get()

    cursor.execute("SELECT role FROM Users WHERE username = %s AND password = %s", (username, password))
    result = cursor.fetchone()

    if result:
        open_main_menu(username, result[0])
        login_window.destroy()
    else:
        messagebox.showerror("Error", "Invalid username or password.")

# Function to handle signup
def signup():
    signup_window = Toplevel()
    signup_window.title("Signup")

    Label(signup_window, text="Username").pack()
    signup_username_entry = Entry(signup_window)
    signup_username_entry.pack()

    Label(signup_window, text="Password").pack()
    signup_password_entry = Entry(signup_window, show="*")
    signup_password_entry.pack()

    Label(signup_window, text="Role (admin/user)").pack()
    signup_role_entry = Entry(signup_window)
    signup_role_entry.pack()

    Button(signup_window, text="Signup", command=lambda: add_user(
        signup_username_entry.get(), signup_password_entry.get(), signup_role_entry.get())).pack()

# --- Login Window ---

login_window = Tk()
login_window.title("Login")
login_window.geometry("300x200")

Label(login_window, text="Username").pack()
username_entry = Entry(login_window)
username_entry.pack()

Label(login_window, text="Password").pack()
password_entry = Entry(login_window, show="*")
password_entry.pack()

Button(login_window, text="Login", command=login).pack()
Button(login_window, text="Signup", command=signup).pack()
Button(login_window, text="Exit", command=login_window.destroy).pack()

# Start the GUI event loop
login_window.mainloop()

# Close the database connection
cursor.close()
conn.close()
