import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.simpledialog import askstring
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

# Database connection
def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='todo'
    )

def add_admin(username, password):
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='todo'
    )
    
# Add an admin user
add_admin('admin', '123')

# Styling constants to mimic the HTML design
FONT_TITLE = ("Inter", 20, "bold")
FONT_NORMAL = ("Inter", 12)
COLOR_PRIMARY = "#1877f2"
COLOR_SECONDARY = "#3b5998"
COLOR_LIGHT = "#f7f7f7"

# Admin Panel
class AdminPanel:
    def __init__(self, root):
        self.root = root
        self.root.title("Admin Panel")
        self.root.configure(bg=COLOR_LIGHT)

        # Admin Panel UI
        header = tk.Label(self.root, text="Admin Panel", font=FONT_TITLE, bg=COLOR_PRIMARY, fg="white")
        header.pack(fill="x", pady=10)

        manage_users_button = ttk.Button(self.root, text="Manage Users", command=self.manage_users)
        manage_users_button.pack(pady=10)

        manage_tasks_button = ttk.Button(self.root, text="Manage Tasks", command=self.manage_tasks)
        manage_tasks_button.pack(pady=10)

        logout_button = ttk.Button(self.root, text="Logout", command=self.logout)
        logout_button.pack(pady=20)

    def manage_users(self):
        UsersManager(self.root)

    def manage_tasks(self):
        TasksManager(self.root, is_admin=True)

    def logout(self):
        self.root.destroy()
        main_screen()

# User Panel
class UserPanel:
    def __init__(self, root, user_id):
        self.root = root
        self.root.title("User Panel")
        self.root.configure(bg=COLOR_LIGHT)
        self.user_id = user_id

        # User Panel UI
        header = tk.Label(self.root, text="User Panel", font=FONT_TITLE, bg=COLOR_PRIMARY, fg="white")
        header.pack(fill="x", pady=10)

        manage_tasks_button = ttk.Button(self.root, text="Manage My Tasks", command=self.manage_my_tasks)
        manage_tasks_button.pack(pady=10)

        logout_button = ttk.Button(self.root, text="Logout", command=self.logout)
        logout_button.pack(pady=20)

    def manage_my_tasks(self):
        TasksManager(self.root, user_id=self.user_id)

    def logout(self):
        self.root.destroy()
        main_screen()

# Manage Users for Admins
class UsersManager:
    def __init__(self, root):
        self.root = root
        self.top = tk.Toplevel(root)
        self.top.title("Manage Users")
        self.top.configure(bg=COLOR_LIGHT)

        tk.Label(self.top, text="Manage Users", font=FONT_TITLE, bg=COLOR_PRIMARY, fg="white").pack(fill="x", pady=10)

        self.tree = ttk.Treeview(self.top, columns=("ID", "Username"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Username", text="Username")
        self.tree.pack(pady=10)

        self.load_users()

        add_user_button = ttk.Button(self.top, text="Add User", command=self.add_user)
        add_user_button.pack(pady=5)

        delete_user_button = ttk.Button(self.top, text="Delete User", command=self.delete_user)
        delete_user_button.pack(pady=5)

    def load_users(self):
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT id, username FROM users")
        users = cursor.fetchall()
        connection.close()

        for user in users:
            self.tree.insert("", tk.END, values=user)

    def add_user(self):
        username = askstring("Add User", "Enter new username:")
        password = askstring("Add User", "Enter new password:")
        if username and password:
            hashed_password = generate_password_hash(password)
            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
            connection.commit()
            connection.close()
            self.tree.insert("", tk.END, values=(cursor.lastrowid, username))
            messagebox.showinfo("Success", "User added successfully!")

    def delete_user(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "No user selected.")
            return

        user_id = self.tree.item(selected_item, "values")[0]
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        connection.commit()
        connection.close()
        self.tree.delete(selected_item)
        messagebox.showinfo("Success", "User deleted successfully!")

# Manage Tasks for Users and Admins
class TasksManager:
    def __init__(self, root, user_id=None, is_admin=False):
        self.root = root
        self.user_id = user_id
        self.is_admin = is_admin
        self.top = tk.Toplevel(root)
        self.top.title("Manage Tasks")
        self.top.configure(bg=COLOR_LIGHT)

        tk.Label(self.top, text="Manage Tasks", font=FONT_TITLE, bg=COLOR_PRIMARY, fg="white").pack(fill="x", pady=10)

        self.tree = ttk.Treeview(self.top, columns=("ID", "Task", "Completed", "Deadline"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Task", text="Task")
        self.tree.heading("Completed", text="Completed")
        self.tree.heading("Deadline", text="Deadline")
        self.tree.pack(pady=10)

        self.load_tasks()

        add_task_button = ttk.Button(self.top, text="Add Task", command=self.add_task)
        add_task_button.pack(pady=5)

        delete_task_button = ttk.Button(self.top, text="Delete Task", command=self.delete_task)
        delete_task_button.pack(pady=5)

    def load_tasks(self):
        connection = get_db_connection()
        cursor = connection.cursor()

        if self.is_admin:
            cursor.execute("SELECT id, task, completed, deadline FROM tasks")
        else:
            cursor.execute("SELECT id, task, completed, deadline FROM tasks WHERE user_id = %s", (self.user_id,))

        tasks = cursor.fetchall()
        connection.close()

        for task in tasks:
            self.tree.insert("", tk.END, values=task)

    def add_task(self):
        task = askstring("Add Task", "Enter task description:")
        deadline = askstring("Add Task", "Enter deadline (YYYY-MM-DD):")
        if task and deadline:
            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO tasks (user_id, task, deadline) VALUES (%s, %s, %s)",
                (self.user_id, task, deadline)
            )
            connection.commit()
            connection.close()
            self.tree.insert("", tk.END, values=(cursor.lastrowid, task, False, deadline))
            messagebox.showinfo("Success", "Task added successfully!")

    def delete_task(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "No task selected.")
            return

        task_id = self.tree.item(selected_item, "values")[0]
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
        connection.commit()
        connection.close()
        self.tree.delete(selected_item)
        messagebox.showinfo("Success", "Task deleted successfully!")

# Login Screen
def main_screen():
    root = tk.Tk()
    root.title("Login")
    root.configure(bg=COLOR_LIGHT)

    tk.Label(root, text="Login", font=FONT_TITLE, bg=COLOR_PRIMARY, fg="white").pack(fill="x", pady=10)

    ttk.Label(root, text="Username:").pack(pady=5)
    username_entry = ttk.Entry(root)
    username_entry.pack(pady=5)

    ttk.Label(root, text="Password:").pack(pady=5)
    password_entry = ttk.Entry(root, show="*")
    password_entry.pack(pady=5)

    def login():
        username = username_entry.get()
        password = password_entry.get()

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Check admin table
        cursor.execute("SELECT * FROM admin_accounts WHERE username = %s", (username,))
        admin = cursor.fetchone()

        

        if admin and check_password_hash(admin['password'], password):
            root.destroy()
            AdminPanel(tk.Tk())
            return

        # Check users table
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password'], password):
            root.destroy()
            UserPanel(tk.Tk(), user_id=user['id'])
            return

        messagebox.showerror("Error", "Invalid username or password.")
        connection.close()

    ttk.Button(root, text="Login", command=login).pack(pady=20)
    root.mainloop()

if __name__ == "__main__":
    main_screen()
