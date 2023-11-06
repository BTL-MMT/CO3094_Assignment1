import sqlite3
import hashlib

con = sqlite3.connect("clientdata.db")
cur = con.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS clientdata (
    id INTEGER PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    ip_addr VARCHAR(255) NOT NULL,
    port INTEGER
)
""")

username1, password1, ip_addr1, port1 = "yan123", hashlib.sha256("yanpwd".encode()).hexdigest(), "192.168.1.122", 56789
username2, password2, ip_addr2, port2 = "minhnhat123", hashlib.sha256("minhnhatpwd".encode()).hexdigest(), "172.17.0.1", 56780

cur.execute("INSERT INTO clientdata (username, password, ip_addr, port) VALUES (?, ?, ?, ?)",
            (username1, password1, ip_addr1, port1))
cur.execute("INSERT INTO clientdata (username, password, ip_addr, port) VALUES (?, ?, ?, ?)",
            (username2, password2, ip_addr2, port2))



con.commit()
con.close()
