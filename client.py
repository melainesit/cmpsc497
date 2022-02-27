
import socket
import json
import threading
from _thread import *
import os


# message #5
def File_Chunk_Request(conn, addr):
    # Parse the message
    # Find the chunk
    # Send the chunk over conn
    receive = conn.recv(4096).decode()
    data = json.loads(receive)
    chunknum = data["chunk"]
    offset = chunknum*1024
    fileName = data["fileName"]
    f.open(fileName,"r")
    f.seek(offset)
    chunkfile = f.read(2014)
    conn.sendto(str.encode(chunkfile),addr)
    return 0 
    # return -1 if failed


def recv_msg(sock):
    #receive = socket.recv(4096).decode('utf-8')
    receive = sock.recv(4096).decode()
    print("this is rec: "+ str(receive))
    #socket.connect((HOST,PORT))
    data = json.loads(receive)
    return data

def send_msg(sock, dic):
    send = json.dumps(dic)
    sock.send(str.encode(send))
    return 0

def start_listener(sock):
    sock.listen()
    while True:
        conn, addr = sock.accept()
        print("Connected by ", addr)
        start_new_thread(File_Chunk_Request, (conn, addr))



# localhost
HOST = '127.0.0.1'  
# Port to listen on    
PORT = 65026
LISTEN_PORT = 65016
print("Waiting for connection")
#with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#sock.listen()
sListen = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sListen.bind((HOST, LISTEN_PORT))
start_new_thread(start_listener, (sListen,))



# Peer format for messages:

# Message 1
# {
#   message: 1,
#   files: [
#       (fileName, fileSize)
#   ]
# }

# Message 2
# {
#   message: 1,
# }

# Message 3
# {
#   message: 1,
#   fileName: fileName
# }

# Message 4
#{
#   message: 4,
#   file: "filename",
#   chunk: chunkNumber
# }

# Message 5
#{
#   message: 5,
#   fileName: "filename",
#   chunk: chunkNumber
# }
ansr = "y"
while ansr=="y":
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    #data = s.recv(4096).decode()
    message = input("What message would you like to send: ")
    message = message.strip()
    msgdict = {}
    
    if message == "1":
        mylist = []
        ans = "y"
        while ans == "y":
            files = input("What file do you want to share: ")
            files = files.strip()
            #f.open(files,"r")
            size = os.path.getsize("./"+files)
            tup = (files, size)
            mylist.append(tup)
            ans = input("Would you like to add another file? (y/n): ")
            ans = ans.strip()
        msgdict["message"] = 1
        msgdict["files"] = mylist
        msgdict["lPort"] = LISTEN_PORT
        send_msg(s,msgdict)
        data = recv_msg(s)
        if data["success"] != 1:
            print("An error has occurred")
    
    
    if message == "2":
        msgdict["message"] = 2
        send_msg(s, msgdict)
        data = recv_msg(s)
        #receive = s.recv(4096).decode()
        #data = json.loads(receive)

    if message == "3":
        fileName = input("What file are you looking for:")
        fileName = fileName.strip()
        msgdict["message"] = 3
        msgdict["fileName"] = fileName
        send_msg(s, msgdict)
        data = recv_msg(s)

    if message == "5":
        fileName = input("What file: ")
        fileName = fileName.strip()
        chunk = input("What chunk number: ")
        chunk = chunk.strip()
        msgdict["message"] = 5
        msgdict["fileName"] = fileName
        msgdict["chunk"] = chunk
        # send the message to the peer (how does it even know what peer)
        send_msg(s, msgdict)
        # receive the chunk 
        recv_msg(s)
        # reformat the message
        msgdict["message"] = 4
        # send the message to the server
        send_msg(s, msgdict)
        # should receive the message that it was successful
        data = recv_msg(s)
        if data["success"] != 1:
            print("An error has occurred")

    s.close()
    ansr = input("Do you want to send another meesage? (y/n): ")
    ansr = ansr.strip()
