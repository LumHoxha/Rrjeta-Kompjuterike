import socket
import threading
import time

MAX_USERS = 2
TIMEOUT = 30  # Timeout in seconds for client inactivity
LOG_FILE = "server_log.txt"
LOGOUT_DELAY = 20  # Delay in seconds before auto-logout

server_ip = '127.0.0.1'
server_port = 12345

clients = {}  # {client_ip: last_active_time}
roles = {"admin": {}, "users": {}}  # Track roles and usernames by IP
client_usernames = {}  # {client_ip: username}
logout_timers = {}  # Timers for auto-logout
lock = threading.Lock()

# Log messages to the server log file
def log_message(client_ip, username, message):
    with open(LOG_FILE, 'a') as log:
        log.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {username} ({client_ip}): {message}\n")

# Handle commands for the admin
# Dictionary to track pending writes (e.g., {client_ip: filename})
pending_writes = {}

def handle_admin(command, client_ip):
    global pending_writes
    args = command.split(' ', 1)

    if args[0] == "CREATE":
        filename = args[1]
        with open(filename, 'w') as f:
            return f"File {filename} created."

    elif args[0] == "WRITE":
        filename = args[1]
        pending_writes[client_ip] = filename  # Mark the file for pending write
        return f"Ready to write to {filename}."

    elif client_ip in pending_writes:  # Handle the content to write
        filename = pending_writes[client_ip]
        content = command  # The entire command is treated as content here
        with open(filename, 'a') as f:  # Append the content to the file
            f.write(content + "\n")
        del pending_writes[client_ip]  # Clear the pending write state
        return f"Content written to {filename}."

    elif args[0] == "READ":
        filename = args[1]
        try:
            with open(filename, 'r') as f:
                return f.read()
        except FileNotFoundError:
            return "File not found."

    elif args[0] == "LIST_USERS":
        with lock:
            connected_users = [f"Admin: {admin_ip}" for admin_ip in roles["admin"]] + \
                               [f"User: {username} ({ip})" for username, ip in roles["users"].items()]
        return "\n".join(connected_users)

    else:
        return "Invalid admin command."

    args = command.split(' ', 1)
    if args[0] == "CREATE":
        filename = args[1]
        with open(filename, 'w') as f:
            return f"File {filename} created."
    elif args[0] == "WRITE":
        filename = args[1]
        return f"Ready to write to {filename}."
    elif args[0] == "READ":
        filename = args[1]
        try:
            with open(filename, 'r') as f:
                return f.read()
        except FileNotFoundError:
            return "File not found."
    elif args[0] == "LIST_USERS":
        with lock:
            connected_users = [f"Admin: {admin_ip}" for admin_ip in roles["admin"]] + \
                              [f"User: {username} ({ip})" for username, ip in roles["users"].items()]
        return "\n".join(connected_users)
    else:
        return "Invalid admin command."
