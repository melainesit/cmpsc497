
import socket
import json
import threading
from _thread import *
import os
import sys
import shutil
from datetime import datetime

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

    # send and receive the data
    send_msg(sock, msgdict)
    data = recv_msg(sock)
    print(data)
    sock.close()

# request all the messages from the server
def request_comments():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    # create the dictionary
    msgdict = {"message": 2}
    send_msg(sock, msgdict)
    data = recv_msg(sock)
    print("These are currently the messages: " + str(data["comment"]))
    
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
# server port   
PORT = int(sys.argv[2])

print("Waiting for connection")

# connect with the server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

while True:
    # checks if the user wants to see all the messages
    allmessages = input("Do you want to see all the messages? (yes/no): ").strip()
    if allmessages == "yes":
        # gets all the messages
        request_comments()
    
    # check if the user wants to send a message
    message = input("Do you want to send a message? (yes/no): ").strip()
    if message == "yes":
        # gets the name of the sender from command line
        sender = sys.argv[1]
        comment = input("Input the message you want to send: ")
        # get the date/time of the message being created
        timestamp = datetime.now()
        timestamp = timestamp.strftime("%d/%m/%Y %H:%M:%S")
        start_new_thread(write, (sender, comment, timestamp))

    # end loop
    if message == "no":
        break



