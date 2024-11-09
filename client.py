import socket

server_ip = '127.0.0.1'
server_port = 12345

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send_message(message):
    client.sendto(message.encode(), (server_ip, server_port))
    response, _ = client.recvfrom(1024)
    print(f"Server response: {response.decode()}")
    return response.decode()

# Ensure this function is defined before admin_menu
def write_to_file(filename):
    response = send_message(f"WRITE {filename}")
    if response.startswith("Ready to write"):
        content = input("Enter content to write: ")
        client.sendto(content.encode(), (server_ip, server_port))
        confirmation, _ = client.recvfrom(1024)
        print(f"Server response: {confirmation.decode()}")

def admin_menu():
    while True:
        print("\nAdmin Menu:")
        print("1. Create file")
        print("2. Write to file")
        print("3. Read file")
        print("4. List connected users")
        print("5. Logout")
        choice = input("Choose an option: ")

        if choice == '1':
            filename = input("Enter filename to create: ")
            send_message(f"CREATE {filename}")
        elif choice == '2':
            filename = input("Enter filename to write to: ")
            write_to_file(filename)
        elif choice == '3':
            filename = input("Enter filename to read: ")
            send_message(f"READ {filename}")
        elif choice == '4':
            send_message("LIST_USERS")
        elif choice == '5':
            print("Logging out...")
            return
        else:
            print("Invalid choice. Try again.")

def user_menu(username):
    while True:
        print("\nUser Menu:")
        print("1. Read file")
        print("2. Logout")
        choice = input("Choose an option: ")

        if choice == '1':
            filename = input("Enter filename to read: ")
            send_message(f"READ {filename}")
        elif choice == '2':
            print("Logging out...")
            return
        else:
            print("Invalid choice. Try again.")
