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

