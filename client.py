
import socket
import json
import threading
from _thread import *
import os
import sys
import shutil
from datetime import datetime



# message #7 to send a message for lab 2
# Message 7 format
#{
#   message: 7,
#   Message: "comment",
#   Timestamp: timestamp
# }

# create the message to send out. Will go to the server first
def write(sender, comment, timestamp):
    # create a socket to send the message to the server
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    # create the dictionary
    msgdict = {"message": 1}
    # sender is just a name
    msgdict["sender"] = sender
    msgdict["comment"] = comment
    msgdict["timestamp"] = timestamp

    # add in sender
    # send and receive the data
    send_msg(sock, msgdict)
    data = recv_msg(sock)
    print(data)
    sock.close()

def request_comments():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    # create the dictionary
    msgdict = {"message": 2}
    send_msg(sock, msgdict)
    data = recv_msg(sock)
    print("These are currently the messages: " + str(data["comment"]))
    #print(type(data))
    #return data
    #print("this is request:" + str(data))
    sock.close()



def recv_msg(sock):
    receive = sock.recv(4096).decode('utf-8')
    data = json.loads(receive)
    return data

def send_msg(sock, dic):
    send = json.dumps(dic)
    sock.send(str.encode(send))
    return 0



# the command line will be:
# $ python3 client.py client1 65000  

# localhost
HOST = '127.0.0.1'  
# Port to listen on 
# server port   
PORT = int(sys.argv[2])

print("Waiting for connection")

# port to listen for peer to peer connection
sListen = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sListen.connect((HOST, PORT))




while True:
    allmessages = input("Do you want to see all the messages ? (yes/no): ").strip()
    if allmessages == "yes":
        request_comments()
    
    
    message = input("Do you want to send a message? (yes/no): ").strip()
    if message == "yes":
        # actual message to send
        #start_new_thread(request_comments, ())
        sender = sys.argv[1]
        comment = input("Input the message you want to send: ")
        timestamp = datetime.now()
        timestamp = timestamp.strftime("%d/%m/%Y %H:%M:%S")
        start_new_thread(write, (sender, comment, timestamp))

    # end loop
    if message == "no":
        break



