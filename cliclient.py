from client import Client
import threading


client = Client()


def help_list():
    print("Authorize your account by: author signin>")
    print("If you do not have account, please sign up: author signup")
    print("To publish a file: publish <lname> <filename>")
    print("To download a file: fetch <filename>")


def handle_command():
    while True:
        if client.server_status:
            message = input("Input command: ")
            if "author" in message:
                mess = message.split(" ")[-1]
                result = client.author(mess)
                if result:
                    print("Successful, continue....")
                else:
                    print("Fail !!!")
            elif "publish" in message:
                lname = message.split(" ")[1]
                fname = message.split(" ")[2]
                result = client.publish(lname, fname)
                if result:
                    print("Publish successful.")
                else:
                    print("Publish fail.")
            elif "fetch" in message:
                mess = message.split(" ")[-1]
                result = client.fetch(mess)
                if result == "1":
                    print("File in your local.")
                elif result == "3":
                    print("Process error.")
                else:
                    print("Download successful: ", result)

            elif "end" in message:
                client.server_status = False
                client.soc_alive.close()
                break
            else:
                break
        else:
            print("Can't connect to the server !!!")
            break

help_list()
handle_command()
