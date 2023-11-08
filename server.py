import socket
import threading
import sqlite3
import hashlib
import json
from flask import Flask, render_template, request, flash, redirect, url_for

HOST = "127.0.0.1"
SERVER_PORT = 56700
FORMAT = "utf8"

isOn = False

class Server:
    def __init__(self):
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.soc.bind((HOST, SERVER_PORT))
        self.soc.listen()
        self.can_publish = False
        print("Server side")
        print("server:", HOST, ":", SERVER_PORT)
        print("waiting")
    
    def handle_client(self, connection, address):
        try:
            while True:
                mess = connection.recv(1024).decode()
                if not mess:
                    break
                print(mess)
                if mess == "CONNECT": 
                    connection.send("RESPONSE 200".encode())
                elif mess == "SIGNIN":
                    self.handle_login(connection, address)
                elif mess == "SIGNUP":
                    self.handle_signup(connection, address)
                elif "ASK" in mess:
                    if mess == "ASK -publish":
                        if self.can_publish == True:
                            connection.send("Give me the lname and fname".encode())
                            mess = connection.recv(1024).decode()
                            mess = json.loads(mess)
                            lname, fname = mess["lname"], mess["fname"]
                            ipaddr = address[0]
                            port = address[1]
                            self.publish(ipaddr, port, lname, fname)
                        else:
                            connection.send("You can't publish any file.")
                    elif mess == "ASK -file":
                        connection.send("Give me the filename.".encode())
                        fname_mess = connection.recv(1024).decode()
                        list = self.discover_file(fname_mess)
                        send = json.dumps(list)
                        connection.send(send.encode())

        except:
            print("eorr")
    
    def connect_client(self):
        nclient = 0
        while nclient < 3 :
            try: 
                connection, address = self.soc.accept()
                thread = threading.Thread(target=self.handle_client, args=(connection,address, ))
                thread.daemon = False
                thread.start()
            except:
                print("errror!!!")
                connection.send("RESPONSE 201".encode())
            nclient +=1

    def take_address(self, username):
        con = sqlite3.connect("clientdata.db")
        cur = con.cursor()
        cur.execute("SELECT ip_addr, port FROM clientdata WHERE username = ?", (username,))
        result = cur.fetchone()
        return result
    def take_lname(self, username, fname):
        con = sqlite3.connect("clientdata.db")
        cur = con.cursor()
        cur.execute(f"SELECT lname FROM {username} WHERE fname = ?", (fname,))
        result = cur.fetchone()
        return result[0]
    def make_dict(self, username, fname):
        try:
            ipaddr, port = self.take_address(username)
            lname = self.take_lname(username, fname)
            dict={}
            dict["ipaddr"], dict["port"] = ipaddr, port
            dict["lname"] = lname
            return dict
        except:
            return None

    def discover_file(self, fname):
        #query list_username
        con = sqlite3.connect("clientdata.db")
        cur = con.cursor()
        cur.execute('SELECT username FROM clientdata')
        username_tuples = cur.fetchall()
        con.close()
        list_username = [username[0] for username in username_tuples]
        #find user have file list username
        user_with_file = []
        for username in list_username:
            print(username)
            list_file = self.discover(username)
            if list_file is None:
                continue
            else:
                if fname in list_file:
                    if self.ping_client(username):
                        user_dict = self.make_dict(username, fname)
                        if user_dict:
                            user_with_file.append(user_dict)
        return user_with_file

    def add_to_database(self, ipaddr, port, lname, fname):
        con = sqlite3.connect("clientdata.db")
        cur = con.cursor()
        cur.execute("SELECT username FROM clientdata WHERE ip_addr = ? and port = ?" , (ipaddr, port))
        result = cur.fetchone()
        if result is not None:
            username = result[0]
        else:
            print("User not found based on the provided IP and port")
            con.close()
            return False
        create_table = f'''
            CREATE TABLE IF NOT EXISTS {username} (
                id INTEGER PRIMARY KEY,
                lname VARCHAR(255) NOT NULL,
                fname VARCHAR(255) NOT NULL
            );
        '''
        cur.execute(create_table)
        cur.execute(f"SELECT fname FROM {username} WHERE fname = ?", (fname,))
        result = cur.fetchone()
        if result is not None:
            cur.execute(f"UPDATE {username} SET lname = ? WHERE fname = ?", (lname, fname))
        else:  
            insert_data = f"INSERT INTO {username} (lname, fname) VALUES (?, ?)"
            cur.execute(insert_data, (lname, fname))
        con.commit()
        con.close()
        return True

    def publish(self, ipaddr,port, lname, fname):
        if self.add_to_database(ipaddr, port, lname, fname):
            print("add_oke")
        else:
            print("add_fail")

    def handle_login(self, c, address):
        con = sqlite3.connect("clientdata.db")
        cur = con.cursor()
        c.send("Username: ".encode())
        username = c.recv(1024).decode()
        c.send("Password: ".encode())
        password = c.recv(1024).decode()
        password = hashlib.sha256(password.encode()).hexdigest()

        cur.execute("SELECT * FROM clientdata WHERE username = ? and password = ?", (username, password))
        if cur.fetchall():
            c.send("Login successful.".encode())
            self.can_publish = True
            #save the new ip and port yo the database
            new_ip_addr = address[0]
            new_port = address[1]
            cur.execute("UPDATE clientdata SET ip_addr = ? WHERE username = ?", (new_ip_addr, username))
            cur.execute("UPDATE clientdata SET port = ? WHERE username = ?", (new_port, username))
            con.commit()
            con.close()
        else:
            c.send("Login fail.".encode())
        
    def handle_signup(self, c, address):
        con = sqlite3.connect("clientdata.db")
        cur = con.cursor()
        c.send("Username: ".encode())
        usname = c.recv(1024).decode()
        c.send("Password: ".encode())
        pwd = c.recv(1024).decode()
        pwd = hashlib.sha256(pwd.encode()).hexdigest()
        if usname != '' and pwd !='':
            cur.execute("SELECT username from clientdata WHERE username = ?", [usname])
            if cur.fetchone() is not None:
                c.send("Signup fail.".encode())
            else:
                pwd = hashlib.sha256(pwd.encode()).hexdigest()
                new_ip_addr = address[0]
                new_port = address[1]                
                cur.execute("INSERT INTO clientdata (username, password, ip_addr, port) VALUES (?,?,?,?)", (usname, pwd, new_ip_addr, new_port))
                con.commit()
                c.send("Signup successful.".encode())
                self.can_publish = True

    def ping_client(self, username):
        user_ipddr, user_port = self.take_address(username)
        soc_ping = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try: 
            soc_ping.connect((user_ipddr, user_port+1)) 
            soc_ping.send(("PING: " + user_ipddr).encode())
            mess_from_server = soc_ping.recv(1024).decode()
            print(mess_from_server)
            soc_ping.close()
            if mess_from_server == '300_alive':
                return True
            return False
        except:
            return False
        
    def discover(self, hostname):
        list_file = []
        con = sqlite3.connect("clientdata.db")
        cur = con.cursor()
        cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (hostname,))
        result = cur.fetchone()
        if result is not None:
            cur.execute(f'SELECT fname FROM {hostname}')
            data = cur.fetchall()
            list_file = [list[0] for list in data]
            con.close()
            return list_file
        return None

    def __del__(self):
        print("server off")
        self.soc.close()

server = Server()
app = Flask(__name__)
# server.connect_client()
@app.route("/")
def home():
    return render_template("server.html")

@app.route('/discover', methods=["POST"])
def display_list():
    hostname = request.form.get("HostName")
    my_array = server.discover(hostname)
    return render_template('server.html', my_array = my_array)
    
@app.route('/ping', methods=["POST"])
def ping_client():
    hostname = request.form.get("HostName")
    status = server.ping_client(hostname)
    return render_template('server.html', status = status)

@app.route('/turn_on_server', methods=["POST"])
def turn_on_server():
    res = request.form.get('onOff')
    if res == 'on' or res == 'ON' or res == 'On' or res == 'oN': 
        server.connect_client()
    return redirect(url_for('home'))

# @app.route('/turn_off_server')
# def turn_off_server():
#     server.turn_off()
#     return 'Server turned off'

if __name__ == "__main__":
    app.run(port=5050)
