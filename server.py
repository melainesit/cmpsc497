
import socket
import threading
import os
from _thread import *

ThreadCount = 0

# localhost
HOST = '127.0.0.1'  
# Port to listen on    
PORT = 65007
    
# main
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
s.bind((HOST,PORT))
s.listen()
    #conn, addr = s.accept()

# handles requests from the individual client by a thread
def socket_target(conn):
    conn.send(str.encode("Hello Client!"))
    while True:
        data = conn.recv(1024)
        reply = 'Server sent this message: ' + data.decode('utf-8') 
        if not data:
            break
        conn.sendall(str.encode(reply))
    conn.close()

#with conn:
#        print('Connected by', addr)
#        while True:
    #        data = conn.recv(1024)
    #        if not data:
    #            break
            # ensures that all data is sent
    #        conn.sendall(data)
    
while True:
    conn, addr = s.accept()
    print("Connected by ", addr)
        #socket_listen.append(conn)
        #threading.Thread(target = socket_target, args = (conns,)).start
    start_new_thread(socket_target, (conn, ))
    ThreadCount +=1
    print("Thread Number: " + str(ThreadCount))
s.close()
