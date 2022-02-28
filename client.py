
import socket
import json
import threading
from _thread import *
import os
import sys


# message #5
def File_Chunk_Request(conn, addr):
    # Parse the message
    # Find the chunk
    # Send the chunk over conn
    receive = conn.recv(4096).decode()
    data = json.loads(receive)
    # format a message to send back
    senddict = {}
    senddict["message"] = 5
    senddict["fileName"] = data["fileName"]
    senddict["chunk"] = data["chunk"]
    # find out what chunk of data to send
    chunknum = data["chunk"]
    offset = (chunknum-1)*1024
    fileName = data["fileName"]
    f = open(fileName,"r")
    f.seek(offset)
    chunkfile = f.read(1024)
    senddict["data"] = chunkfile
    y = json.dumps(senddict)
    conn.sendto(str.encode(y),addr)
    return 0 
    # return -1 if failed


def recv_msg(sock):
    #receive = socket.recv(4096).decode('utf-8')
    receive = sock.recv(4096).decode('utf-8')
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
PORT = int(sys.argv[1])
LISTEN_PORT = int(sys.argv[2])
fileList = {}
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
#   fileName: "filename",
#   chunk: chunkNumber
# }

# Message 5
#{
#   message: 5,
#   fileName: "filename",
#   chunk: chunkNumber
# }
#ansr = "y"
while True:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    #data = s.recv(4096).decode()
    message = input("What message would you like to send: ").strip()
    msgdict = {}
    
    if message == "1":
        mylist = []
        ans = "y"
        while ans == "y":
            files = input("What file do you want to share: ").strip()
            #f.open(files,"r")
            size = os.path.getsize("./"+files)
            tup = (files, size)
            mylist.append(tup)
            ans = input("Would you like to add another file? (y/n): ").strip()
        msgdict["message"] = 1
        msgdict["files"] = mylist
        msgdict["lPort"] = LISTEN_PORT
        send_msg(s,msgdict)
        data1 = recv_msg(s)
        print("This is data1: " + str(data1))
        if data1["success"] != 1:
            print("An error has occurred")
    
    
    if message == "2":
        msgdict["message"] = 2
        send_msg(s, msgdict)
        data2 = recv_msg(s)
        for lfile in data2["files"].keys():
            fileList[lfile] = data2["files"][lfile]
        #print(fileList)
        #receive = s.recv(4096).decode()
        #data = json.loads(receive)

    if message == "3":
        fileName = input("What file are you looking for: ").strip()
        msgdict["message"] = 3
        msgdict["fileName"] = fileName
        send_msg(s, msgdict)
        data3 = recv_msg(s)

    if message == "5":
        listoffiles = []
        listofchunks = []
        # checks if the file list has files, else run message 2
        if len(fileList)==0:
            tempSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tempSock.connect((HOST, PORT))
            msgdict["message"] = 2
            send_msg(tempSock, msgdict)
            data2 = recv_msg(tempSock)
            for lfile in data2["files"].keys():
                fileList[lfile] = data2["files"][lfile]
            tempSock.close()
            

        print("This is the fileList: " + str(fileList))


        # makes a list of just the file names
        for key in fileList.keys():
            listoffiles.append(key)
        #print("this is fileList: " + str(fileList))
        # offer that list to the user and ask them to pick off that list
        #print("Here are a list of files to choose from:" + str(listoffiles))
        print("Here are a list of files to choose from:" )
        for i in range(len(listoffiles)):
            fi = listoffiles[i]
            i+=1
            print(str(i) + ".\t" + str(fi))

        fileNum = int(input("What file do you want: ").strip())
        fileName = listoffiles[fileNum-1]
        # checks if the fileName exists in the list of files
        while fileName not in listoffiles:
            print("File not found or incorrectly typed, try again")
            fileName = input("What file do you want: ").strip()

        # remove the length to get only the chunk list

        # goes through the chunks and combines them into a list
        for key in fileList[fileName].keys():
            listofchunks+=fileList[fileName][key]
        # Removes the duplicate chunks
        listofchunks = list(set(listofchunks))
        # offers the list of chunks to the user and asks them to pick off that list
        print("This is list of chunks: " + str(listofchunks))
        chunk = int(input("What chunk number do you want: ").strip())
        # checks if the chunk number is in the list
        while chunk not in listofchunks:
            print("Chunk not found or incorrectly typed, try again.")
            chunk = int(input("What chunk number do you want: ").strip())

        # run message 3 to find out what peer has that chunk
        fileowners = []
        #for peer in
        tempSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tempSock.connect((HOST, PORT))
        msgdict["message"] = 3
        msgdict["fileName"] = fileName
        send_msg(tempSock, msgdict)
        data3 = recv_msg(tempSock)
        #print("This is data3: " + str(data3))

        # go find a peer that has that chunk
        for peer in data3["peers"].keys():
            if chunk in data3["peers"][peer]:
                fileowners.append(peer)

        print("Choose one of these peers to receive the data from: ")
        # enumerate to make it easier for the peer to select
        for i in range(len(fileowners)):
            peer = fileowners[i]
            i+=1
            print(str(i) + ".\t" + str(peer))

        peernum = int(input("Enter which peer you want to receive data from:" ).strip())
        peer = fileowners[peernum-1]
        print("this is peer= " + str(peer))
        while peer not in fileowners:
            print("Peer not found or incorrectly typed, try again.")
            peer = input("Choose one of these peers to receive the data from: ").strip()

        peer = peer.split(":")

        tempSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tempSock.connect((peer[0],int(peer[1])))
        msgdict["message"] = 5
        msgdict["fileName"] = fileName
        msgdict["chunk"] = chunk
        msgdict["peer"] = peer

        # send the message to the peer (how does it even know what peer)
        send_msg(tempSock, msgdict)
        # receive the chunk 
        newdata = recv_msg(tempSock)
        path = input("Where would you like to save the file? ")
        f = open("./"+path, "w+")
        f.seek((chunk-1)*1024)
        f.write(newdata["data"])
        f.close()
        print("Success for messsage 5.. Now onto message 4")

        # reformat the message
        msgdict["message"] = 4
        msgdict["fileName"] = fileName
        msgdict["chunk"] = chunk
        msgdict["lPort"] = LISTEN_PORT
        # send the message to the server
        send_msg(s, msgdict)
        print("print1")
        # should receive the message that it was successful
        data = recv_msg(s)
        if data["success"] != 1:
            print("An error has occurred")
    if message == "6":
        break
    s.close()


# Message 4
#{
#   message: 4,
#   file: "filename",
#   chunk: chunkNumber
# }

    #s.close()
    #ansr = input("Do you want to send another meesage? (y/n): ")
    #ansr = ansr.strip()
