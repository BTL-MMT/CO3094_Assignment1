import socket
import threading
import json

HOST = "127.0.0.1"
SERVER_PORT = 56700
FORMAT = "utf8"


class Client:
    def __init__(self):
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print("Client side")
        self.server_status = self.connect_server()

    def connect_server(self):
        try:
            self.soc.connect((HOST, SERVER_PORT))
            ipaddr, port = self.soc.getsockname()

            self.soc_alive = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.soc_alive.bind((ipaddr, port + 1))
            self.soc_alive.listen(1)

            print("client address:", ipaddr, ":", port)
            self.soc.send("CONNECT".encode())
            mess_from_server = self.soc.recv(1024).decode()
            print(mess_from_server)
            if mess_from_server == 'RESPONSE 200':
                return True
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    def signin_client(self):
        self.soc.send("SIGNIN".encode())
        mess_from_server = self.soc.recv(1024).decode()
        self.soc.send(input(mess_from_server).encode())
        mess_from_server = self.soc.recv(1024).decode()
        self.soc.send(input(mess_from_server).encode())

        mess_from_server = self.soc.recv(1024).decode()
        print(mess_from_server)
        if mess_from_server == "Login successful.":
            return True
        return False

    def signup_client(self):
        self.soc.send("SIGNUP".encode())
        mess_from_server = self.soc.recv(1024).decode()
        self.soc.send(input(mess_from_server).encode())
        mess_from_server = self.soc.recv(1024).decode()
        self.soc.send(input(mess_from_server).encode())

        mess_from_server = self.soc.recv(1024).decode()
        print(mess_from_server)
        if mess_from_server == "Signup successful.":
            return True
        return False

    def alive(self):
        try:
            print("I'm waiting for you...")
            server_soc, address = self.soc_alive.accept()
            mess = server_soc.recv(1024).decode()
            print(mess)
            server_soc.send("300_alive".encode())
            server_soc.close()
        except socket.error as e:
            server_soc.send("301_dead".encode())
            print(f"Error: {e}")

    def author (self, message):
        if message == "signin":
            if self.signin_client():
                thread = threading.Thread(target=client.alive)
                thread.daemon = False
                thread.start()
            else:
                print("login fail")
        else:
            if self.signup_client():
                thread = threading.Thread(target=client.alive)
                thread.daemon = False
                thread.start()
            else: 
                print("signup fail")
    
    def publish(self, lname, fname):
        self.soc.send("ASK -publish".encode())
        try:
            mess_from_server = self.soc.recv(1024).decode()
            if mess_from_server == "Give me the lname and fname":
                to_send = {"lname": lname, "fname": fname}
                to_send = json.dumps(to_send)
                self.soc.send(to_send.encode())
            elif mess_from_server == "You can't publish any file":
                print("oke khong publish nua")
        except:
            print("erroroororororo")
            
    def fetch (self, fname):
        self.soc.send("ASK -file".encode())
        try:
            mess_from_server = self.soc.recv(1024).decode()
            print(mess_from_server)
            if mess_from_server == "Give me the filename.":
                self.soc.send(fname.encode())
        except:
            print("ask file errror")

    def __del__(self):
        print("client off !!")
        self.soc.close()

client = Client()
if client.server_status:
    client.author("signin")
    client.publish("c:/meomeo", "meomeomeo")
    client.fetch("meomeomeo")




