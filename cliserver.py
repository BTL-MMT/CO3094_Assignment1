from server import Server
import threading


server = Server()


def help_list():
    print("To see the list file of an username: discover <username>")
    print("To check active status: ping <username>")


def handle_command():
    while True:
        message = input("Input command: ")

        if "ping" in message:
            username = message.split(" ")[-1]
            ping = server.ping_client(username)

            if ping:
                print(username + " is alive")
            else:
                print(username + " is dead")
        elif "discover" in message:
            username = message.split(" ")[-1]
            list_file = server.discover(username)

            if list_file:
                print(list_file)
        elif "end" in message:
            server.status = False
            server.soc.close()
            break

help_list()

thread = threading.Thread(target=handle_command)

thread.daemon = False

thread.start()

server.connect_client()


# print(server.ping_client("yan123"))
