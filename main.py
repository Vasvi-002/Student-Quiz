import tkinter as tk
from tkinter import messagebox
import db

def show_login():
    # 1. Create the main window
    root = tk.Tk()
    root.title("Quiz System - Login")
    root.geometry("400x450")
    root.configure(bg="#1e1e2e")  # Dark background color

    # 2. Add a big title label
    title_label = tk.Label(root, text="📝 Quiz System", font=("Arial", 28, "bold"), bg="#1e1e2e", fg="white")
    title_label.pack(pady=30)

    # 3. Add Username label and entry field
    user_label = tk.Label(root, text="Username:", font=("Arial", 12), bg="#1e1e2e", fg="white")
    user_label.pack()
    
    user_entry = tk.Entry(root, font=("Arial", 14), width=20)
    user_entry.pack(pady=5)

    # 4. Add Password label and entry field (with show="*")
    pass_label = tk.Label(root, text="Password:", font=("Arial", 12), bg="#1e1e2e", fg="white")
    pass_label.pack()
    
    pass_entry = tk.Entry(root, font=("Arial", 14), width=20, show="*")
    pass_entry.pack(pady=5)

    # 5. Define what happens when the login button is clicked
    def login_action():
        # Get the text the user typed
        username = user_entry.get()
        password = pass_entry.get()

        # Check if empty
        if username == "" or password == "":
            messagebox.showerror("Error", "Please fill in both fields.")
            return

        # Check with database
        user_data = db.get_user(username, password)
        
        if user_data is None:
            messagebox.showerror("Error", "Wrong username or password.")
        else:
            # Login successful! Close this window
            root.destroy()
            
            user_id = user_data[0]
            username = user_data[1]
            role = user_data[3]
            
            # Open the correct dashboard based on role
            if role == "admin":
                import admin
                admin.show_admin(user_id, username)
            else:
                import student
                student.show_student(user_id, username)

    # 6. Add the Login button
    login_btn = tk.Button(root, text="Login", font=("Arial", 12, "bold"), command=login_action, width=15)
    login_btn.pack(pady=20)

    # 7. Add a function to switch to the Register screen
    def go_to_register():
        root.destroy()
        show_register()

    # 8. Add the Register button
    reg_btn = tk.Button(root, text="New Student? Register", font=("Arial", 10), command=go_to_register)
    reg_btn.pack()

    # Start the window
    root.mainloop()


def show_register():
    # 1. Create the register window
    root = tk.Tk()
    root.title("Create Account")
    root.geometry("400x450")
    root.configure(bg="#1e1e2e")

    # 2. Add title
    title_label = tk.Label(root, text="➕ Create Account", font=("Arial", 24, "bold"), bg="#1e1e2e", fg="white")
    title_label.pack(pady=30)

    # 3. Add Username field
    user_label = tk.Label(root, text="Choose Username:", font=("Arial", 12), bg="#1e1e2e", fg="white")
    user_label.pack()
    
    user_entry = tk.Entry(root, font=("Arial", 14), width=20)
    user_entry.pack(pady=5)

    # 4. Add Password field
    pass_label = tk.Label(root, text="Choose Password:", font=("Arial", 12), bg="#1e1e2e", fg="white")
    pass_label.pack()
    
    pass_entry = tk.Entry(root, font=("Arial", 14), width=20, show="*")
    pass_entry.pack(pady=5)

    # 5. Define registration action
    def register_action():
        username = user_entry.get()
        password = pass_entry.get()

        if username == "" or password == "":
            messagebox.showerror("Error", "Both fields are required.")
            return
            
        if len(password) < 4:
            messagebox.showerror("Error", "Password must be at least 4 chars long.")
            return
            
        if db.username_exists(username):
            messagebox.showerror("Error", "Username is already taken.")
            return

        # Save to database
        db.register_user(username, password)
        messagebox.showinfo("Success", f"Account created for {username}! You can now login.")
        
        # Go back to login
        root.destroy()
        show_login()

    # 6. Add the Register button
    reg_btn = tk.Button(root, text="Create Account", font=("Arial", 12, "bold"), command=register_action, width=15)
    reg_btn.pack(pady=20)

    # 7. Add Back to Login button
    def go_back():
        root.destroy()
        show_login()

    back_btn = tk.Button(root, text="Go Back to Login", font=("Arial", 10), command=go_back)
    back_btn.pack()

    # Start the window
    root.mainloop()


if __name__ == "__main__":
    show_login()
