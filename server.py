
import socket
import threading
import os
from _thread import *
import json
import math
import sys
from threading import Thread, Lock

 


def write_to_server(servSock, sender, comment, timestamp):
    msgdict = {
        "message": 3,
        "sender": sender,
        "comment": comment,
        "timestamp": timestamp
    }
    y = json.dumps(msgdict)
    servSock.sendto(str.encode(y),addr)
    return 0

    # add the message
    # send it to all the other servers
    # send a message back to the client saying it was sent to all the servers

# send a message back to the client saying that it was sent to all the connections (allConn)
def write_to_client(conn,addr,sender, comment,timestamp,success):
    msgdict = {
        "message": 1,
        "sender": sender,
        "comment": comment,
        "timestamp": timestamp,
        "success": 1
    }
    y = json.dumps(msgdict)
    conn.sendto(str.encode(y), addr)
    return 0


# the client is requesting all the messages
def request_all_comments(conn,addr):
    msgdict = {
        "message": 2,
        "comment": allmessages,
    }
    y = json.dumps(msgdict)
    conn.sendto(str.encode(y),addr)
    return 0

#def sort_dict(mydict):

#    new_list = sorted(mydict.items(), key=lambda x:x[0])
#    mydict = dict(new_list)

# handles requests from the individual client within a thread
def handle_conn(conn, peer):
    global allmessages

    data = conn.recv(4096).decode()
    data = json.loads(data)
    message = data["message"]

    mutex.acquire()
    # client wants to send a message to the server for all servers
    if message == 1:
        sender = data["sender"]
        comment = data["comment"]
        timestamp = data["timestamp"]
        # format a dictionary to append to the messages list {"timestamp" : (sender,message)}
        allmessages[timestamp] = (sender,comment)
        # sort the dictionary
        new_list = sorted(allmessages.items(), key=lambda x:x[0])
        allmessages = dict(new_list)
        print("this is all messages: " + str(allmessages))

        # Check if there are any servers connected before trying to send out the message
        if len(allConn)==0:
            success = -1
            # write to the client that there is no one to send it to.
            # with a message like no one to send it to
            write_to_client(conn,peer,sender, comment,timestamp,success)
        else:
            # loop through conn list and start a new thread and send the message
            for server in allConn:
                #print("this is server:" + str(server))
                servSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                servSock.connect(('127.0.0.1', int(server)))
                start_new_thread(write_to_server, (servSock,sender,comment,timestamp))
            # tell the client that it was successful
            success = 0
            write_to_client(conn,peer,sender, comment,timestamp,success)

    if message == 2:
        #servSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #servSock.connect(('127.0.0.1', int(server)))
        request_all_comments(conn,peer)
        

    # client wants to see all the messages ever made
    #if message == 2:
    #    request_all_comments(conn,peer)

    # server is receiving a message
    if message == 3:
        sender = data["sender"]
        comment = data["comment"]
        timestamp = data["timestamp"]
        # add the message into allmessages
        allmessages[timestamp] = (sender,comment)
        # sort the dictionary
        new_list = sorted(allmessages.items(), key=lambda x:x[0])
        allmessages = dict(new_list)
        print("these are all the messages: " + str(allmessages))
        
    mutex.release()

    conn.close()

    
# a list of all server connections, tuple(conn,addr)
allConn = []
# a dictionary of all messages key = timestamp value: sender, and comment
allmessages = {}
# a lock for multithreading
mutex = Lock()

# the command line will be:
# $ python3 server.py server1 65000


# localhost
HOST = '127.0.0.1'  
# Port to listen on    
PORT = int(sys.argv[2])
    
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((HOST,PORT))
print("Waiting for a connection")
sock.listen()

while True:
    conn, addr = sock.accept()
    print("Connected by ", addr)
    who = sys.argv[1]
    # can just have server.py
    for i in range(3,len(sys.argv)):
        allConn.append(sys.argv[i])
    allConn = list(set(allConn))
    print("this is the connections: " + str(allConn))

    # already handles server-to-server and server-to-client connections
    # this will be listening and receive messages already
    start_new_thread(handle_conn, (conn, addr))
sock.close()
 