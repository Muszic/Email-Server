import tkinter as tk
from tkinter import messagebox, scrolledtext
import sys, os
sys.path.append(os.path.abspath("../server"))
from auth import login
import sqlite3
import socket

DB_PATH = "../db/email_server.db"

def attempt_login():
    username = username_entry.get()
    password = password_entry.get()

    if login(username, password):
        root.destroy()
        open_inbox(username)
    else:
        messagebox.showerror("Login Failed", "Invalid username or password.")

def logout(window):
    window.destroy()
    os.execl(sys.executable, sys.executable, *sys.argv)


def open_inbox(username):
    inbox = tk.Tk()
    inbox.title(f"{username}'s Inbox - MailNest")
    inbox.geometry("500x400")

    tk.Label(inbox, text=f"📥 Inbox for {username}", font=("Arial", 14)).pack(pady=10)

    # Load emails from DB
    emails = fetch_emails(username)
    for mail in emails:
        tk.Label(inbox, text=f"From: {mail[1]}\n{mail[3][:50]}...", anchor='w', justify='left').pack(pady=5)

    tk.Button(inbox, text="Compose", command=lambda: open_compose(username)).pack(pady=10)
    #tk.Button(inbox, text="Compose", command=lambda: open_compose(username)).pack(pady=10)
    tk.Button(inbox, text="Logout", command=lambda: logout(inbox)).pack(pady=5)


    inbox.mainloop()

def fetch_emails(username):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM emails WHERE to_address=?", (username,))
    emails = cursor.fetchall()
    conn.close()
    return emails

import threading

def send_email(username, to, subject, msg, comp):
    def threaded_send():
        full_msg = f"Subject: {subject}\n\n{msg}"
        try:
            s = socket.socket()
            s.connect(("127.0.0.1", 1025))
            s.recv(1024)

            s.send(b"HELO mailnest\r\n")
            s.recv(1024)

            s.send(f"MAIL FROM:<{username}>\r\n".encode())
            s.recv(1024)

            s.send(f"RCPT TO:<{to}>\r\n".encode())
            s.recv(1024)

            s.send(b"DATA\r\n")
            s.recv(1024)

            s.send(full_msg.encode() + b"\r\n.\r\n")
            s.recv(1024)

            s.send(b"QUIT\r\n")
            s.close()

            messagebox.showinfo("Success", "Email sent successfully!")
            comp.destroy()

        except Exception as e:
            print("Error:", e)
            messagebox.showerror("Error", "Failed to send email.")

    # Run the above logic in a thread so GUI doesn't freeze
    threading.Thread(target=threaded_send).start()



def open_compose(username):
    comp = tk.Toplevel()
    comp.title("Compose Email")
    comp.geometry("400x400")

    tk.Label(comp, text="To:").pack()
    to_entry = tk.Entry(comp)
    to_entry.pack()

    tk.Label(comp, text="Subject:").pack()
    subject_entry = tk.Entry(comp)
    subject_entry.pack()

    tk.Label(comp, text="Message:").pack()
    msg_box = scrolledtext.ScrolledText(comp, height=10)
    msg_box.pack()

    # 👇 Correct lambda passes entries and window to send_email
    tk.Button(
        comp,
        text="Send",
        command=lambda: send_email(
            username,
            to_entry.get(),
            subject_entry.get(),
            msg_box.get("1.0", tk.END),
            comp  # this is the key part
        )
    ).pack(pady=10)


def open_signup():
    signup_win = tk.Toplevel()
    signup_win.title("Sign Up - MailNest")
    signup_win.geometry("300x200")

    tk.Label(signup_win, text="New Username").pack()
    new_user = tk.Entry(signup_win)
    new_user.pack()

    tk.Label(signup_win, text="New Password").pack()
    new_pass = tk.Entry(signup_win, show="*")
    new_pass.pack()

    def handle_signup():
        from auth import signup  # import signup function
        if signup(new_user.get(), new_pass.get()):
            messagebox.showinfo("Success", "Signup successful! You can now login.")
            signup_win.destroy()
        else:
            messagebox.showerror("Error", "Username already exists!")

    tk.Button(signup_win, text="Register", command=handle_signup).pack(pady=10)


# ---------------- GUI Login -------------------
root = tk.Tk()
root.title("MailNest - Login")
root.geometry("300x200")

tk.Label(root, text="Username").pack(pady=5)
username_entry = tk.Entry(root)
username_entry.pack()

tk.Label(root, text="Password").pack(pady=5)
password_entry = tk.Entry(root, show="*")
password_entry.pack()

tk.Button(root, text="Login", command=attempt_login).pack(pady=15)

tk.Button(root, text="Sign Up", command=open_signup).pack()

root.mainloop()

