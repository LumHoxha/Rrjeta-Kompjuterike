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
    
    # Handle commands for regular users
def handle_user(command, username):
    args = command.split(' ', 1)
    if args[0] == "READ":
        filename = args[1]
        try:
            with open(filename, 'r') as f:
                return f.read()
        except FileNotFoundError:
            return "File not found."
    else:
        return "Permission denied. Users can only read files."

# Logout users after timeout
def logout_user(client_ip):
    with lock:
        if client_ip in roles["admin"]:
            del roles["admin"][client_ip]
        elif client_ip in roles["users"].values():
            username = next(user for user, ip in roles["users"].items() if ip == client_ip)
            del roles["users"][username]
        if client_ip in clients:
            del clients[client_ip]
        if client_ip in client_usernames:
            del client_usernames[client_ip]
        if client_ip in logout_timers:
            del logout_timers[client_ip]
    print(f"User {client_ip} logged out automatically after {LOGOUT_DELAY} seconds.")

# Handle client requests
def handle_client(data, addr):
    client_ip = addr[0]
    message = data.decode()

    # Track the username for logging and permission checking
    if client_ip in client_usernames:
        username = client_usernames[client_ip]
    else:
        username = "Unknown"

    log_message(client_ip, username, message)  # Log the message with the current username

    # Process login commands
    if message.startswith("LOGIN"):
        _, role, username_input = message.split(' ', 2)

        if role == "admin":
            client_usernames[client_ip] = "admin"
            roles["admin"][client_ip] = "admin"
            print(f"Admin logged in from {client_ip}")
            return f"Admin login successful."

        elif role == "user":
            if len(roles["users"]) < MAX_USERS:
                roles["users"][username_input] = client_ip
                client_usernames[client_ip] = username_input

                # Start a timer to auto-logout the user after LOGOUT_DELAY seconds
                if client_ip in logout_timers:
                    logout_timers[client_ip].cancel()
                logout_timers[client_ip] = threading.Timer(LOGOUT_DELAY, logout_user, [client_ip])
                logout_timers[client_ip].start()

                print(f"User {username_input} logged in from {client_ip}")
                return f"User {username_input} login successful."
            else:
                return "Maximum user connections reached."
        else:
            return "Invalid role."

    # After login, identify role again
    if client_ip in roles["admin"]:
        username = "admin"
    elif client_ip in roles["users"].values():
        username = next(user for user, ip in roles["users"].items() if ip == client_ip)
    else:
        return "Unauthorized. Please login first."

    # Debug output to check role handling
    print(f"Current role for {client_ip} is '{username}'.")

    # Handle admin or user requests based on the logged-in role
    if username == "admin":
        return handle_admin(message, client_ip)
    elif username != "Unknown":
        return handle_user(message, username)
    else:
        return "Unauthorized. Please login first."
    client_ip = addr[0]
    message = data.decode()

    if client_ip in client_usernames:
        username = client_usernames[client_ip]
    else:
        username = "Unknown"

    log_message(client_ip, username, message)  # Log each client message

    if message.startswith("LOGIN"):
        _, role, username_input = message.split(' ', 2)
        if role == "admin":
            client_usernames[client_ip] = "admin"
            roles["admin"][client_ip] = "admin"
            return f"Admin login successful."
        elif role == "user":
            if len(roles["users"]) < MAX_USERS:
                roles["users"][username_input] = client_ip
                client_usernames[client_ip] = username_input
                if client_ip in logout_timers:
                    logout_timers[client_ip].cancel()
                logout_timers[client_ip] = threading.Timer(LOGOUT_DELAY, logout_user, [client_ip])
                logout_timers[client_ip].start()
                return f"User {username_input} login successful."
            else:
                return "Maximum user connections reached."
        else:
            return "Invalid role."

    if client_ip in roles["admin"]:
        username = "admin"
    elif client_ip in roles["users"].values():
        username = next(user for user, ip in roles["users"].items() if ip == client_ip)
    else:
        return "Unauthorized. Please login first."

    if username == "admin":
        return handle_admin(message, client_ip)
    elif username != "Unknown":
        return handle_user(message, username)
    else:
        return "Unauthorized. Please login first."

# Remove inactive clients after a timeout
def remove_inactive_clients():
    while True:
        time.sleep(5)
        current_time = time.time()
        to_remove = []

        with lock:
            for client_ip, last_active in clients.items():
                if current_time - last_active > TIMEOUT:
                    to_remove.append(client_ip)

        for client_ip in to_remove:
            print(f"Disconnecting inactive client: {client_ip}")
            logout_user(client_ip)

# Start server
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind((server_ip, server_port))

print(f"Server listening on {server_ip}:{server_port}")

# Start a thread to clean up inactive clients
threading.Thread(target=remove_inactive_clients, daemon=True).start()

while True:
    try:
        data, addr = server.recvfrom(1024)
        client_ip = addr[0]

        with lock:
            clients[client_ip] = time.time()

        response = handle_client(data, addr)
        server.sendto(response.encode(), addr)
    except Exception as e:
        print(f"Error: {e}")
        break