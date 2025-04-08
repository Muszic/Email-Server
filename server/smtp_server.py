# smtp_server.py
import socket
import os
import sqlite3
from datetime import datetime

HOST = '127.0.0.1'
PORT = 1025
MAILBOX_DIR = "../db/user_emails"

# Ensure mailbox directory exists
os.makedirs(MAILBOX_DIR, exist_ok=True)



def save_email(to_address, from_address, content):
    conn = sqlite3.connect("../db/email_server.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO emails (from_address, to_address, message)
        VALUES (?, ?, ?)
    """, (from_address, to_address, content))

    conn.commit()
    conn.close()
    print(f"[+] Email stored in DB for {to_address}")


def handle_client(client_socket):
    client_socket.send(b"220 MailNest SMTP Server Ready\r\n")
    
    from_address = None
    to_address = None
    message_lines = []
    state = 'INIT'

    while True:
        data = client_socket.recv(1024).decode().strip()
        print(f"Client: {data}")

        if data.upper().startswith("HELO"):
            client_socket.send(b"250 Hello, MailNest welcomes you!\r\n")

        elif data.upper().startswith("MAIL FROM:"):
            from_address = data[10:].strip("<>")
            client_socket.send(b"250 OK\r\n")
            state = 'MAIL_FROM'

        elif data.upper().startswith("RCPT TO:"):
            to_address = data[8:].strip("<>")
            client_socket.send(b"250 OK\r\n")
            state = 'RCPT_TO'

        elif data.upper() == "DATA":
            client_socket.send(b"354 End message with '.' on a line by itself\r\n")
            message_lines = []
            while True:
                line = client_socket.recv(1024).decode().strip()
                if line == ".":
                    break
                message_lines.append(line)
            content = "\n".join(message_lines)
            save_email(to_address, from_address, content)
            client_socket.send(b"250 Message accepted for delivery\r\n")

        elif data.upper() == "QUIT":
            client_socket.send(b"221 Closing connection. Bye!\r\n")
            break

        else:
            client_socket.send(b"502 Command not implemented\r\n")

    client_socket.close()

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f"[✓] SMTP Server running on {HOST}:{PORT}...")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"[+] Connection from {addr}")
        handle_client(client_socket)

if __name__ == "__main__":
    start_server()

