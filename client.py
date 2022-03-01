
import socket
import json
import threading
from _thread import *
import os
import sys
import shutil

# Message 1 format
# {
#   message: 1,
#   files: [
#       (fileName, fileSize)
#   ]
# }
def message1():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    # list of files that will be shared with the server
    mylist = []
    # get the files from the command line arguments
    for arg in range(4, len(sys.argv)):
        size = os.path.getsize(CLIENT_DIR+sys.argv[arg])
        # tuples of the file name and the size of the file
        tup = (sys.argv[arg], size)
        mylist.append(tup)
    # format the message to send
    msgdict = {"message": 1}
    msgdict["files"] = mylist
    msgdict["lPort"] = LISTEN_PORT
    send_msg(sock,msgdict)
    data = recv_msg(sock)
    print(data)
    if data["success"] != 1:
        print("An error has occurred")
    sock.close()
    return data


# Message 2 format
# {
#   message: 2,
# }
def message2():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    # format message to send
    msgdict = {"message": 2}
    send_msg(sock, msgdict)
    data = recv_msg(sock)
    print(data)
    # a list of file names and the peers that have chunks of those files
    for lfile in data["files"].keys():
        fileList[lfile] = data["files"][lfile]
    print("This is fileList: " + str(fileList))
    sock.close()
    return 0

# Message 3 format
# {
#   message: 3,
#   fileName: fileName
# }
# Asks the server for the list of files
# Returns the number of files in the list; and for each file, a file name and a file length.
def message3():
    # get the list of files
    message2()
    # just the file names from fileList
    listoffiles = []
    for key in fileList.keys():
        listoffiles.append(key)

    # offer that list to the user and ask them to pick off that list
    print("Here are a list of files to choose from:" )
    # for error checking to make sure that the user picks a number from the list
    tempindexlist = []
    for i in range(len(listoffiles)):
        fi = listoffiles[i]
        i+=1
        tempindexlist.append(i)
        print(str(i) + ".\t" + str(fi))

    fileNum = int(input("What file are you looking for: ").strip())
    
    # checks if the fileName exists in the list of files
    while fileNum not in tempindexlist:
        print("File not found, try again")
        fileNum = int(input("What file do you want: ").strip())
    fileName = listoffiles[fileNum-1]

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    #format message 3
    msgdict = {"message": 3}
    msgdict["fileName"] = fileName
    print("this is msgdict3: " + str(msgdict))
    send_msg(sock, msgdict)
    data = recv_msg(sock)
    print(data)
    sock.close()
    return data

# Message 4 format
#{
#   message: 4,
#   fileName: "filename",
#   chunk: chunkNumber
# }
# Tells the server when a peer receives a new chunk of the file and becomes a source (of that chunk) for other peers.
def message4(fileName, chunk):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    # format message 4
    msgdict = {"message": 4}
    msgdict["fileName"] = fileName
    msgdict["chunk"] = chunk
    msgdict["lPort"] = LISTEN_PORT
    send_msg(sock, msgdict)
    data = recv_msg(sock)
    print(data)

    # should receive the message that it was successful
    if data["success"] != 1:
        print("An error has occurred")
    sock.close()
    return 0

# Message 5 format
#{
#   message: 5,
#   fileName: "filename",
#   chunk: chunkNumber
# }
def message5():
    # total list of chunks for that file from all peers
    listofchunks = []
   
    # checks if the file list has files, else run message 2
    if len(fileList)==0:
        message2()
            
    print("This is the fileList: " + str(fileList))
    # getting the ip addresses and chunks of a requested file
    data3 = message3()

    fileName = data3['fileName']

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
        
    print("this is data3: " + str(data3))
    # go find a peer that has that chunk
    for peer in data3["peers"].keys():
        if chunk in data3["peers"][peer]:
            fileowners.append(peer)

    print("Choose one of these peers to receive the data from: ")
    # list to keep track of indexes
    tempindexlist = []
    # make it easier for the peer to select
    for i in range(len(fileowners)):
        peer = fileowners[i]
        i+=1
        tempindexlist.append(i)
        print(str(i) + ".\t" + str(peer))

    print(tempindexlist)
    peernum = int(input("Enter which peer you want to receive data from:" ).strip())
    # error check to see if the peer they requested was offered
    while peernum not in tempindexlist:
        print("Peer not found or incorrectly typed, try again.")
        peernum = int(input("Choose one of these peers to receive the data from: ").strip())

    peer = fileowners[peernum-1]
    peer = peer.split(":")

    # Ask the peer for the file chunks
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((peer[0], int(peer[1])))
    msgdict = {}
    msgdict["message"] = 5
    msgdict["fileName"] = fileName
    msgdict["chunk"] = chunk
    msgdict["peer"] = peer
    send_msg(sock, msgdict)
    newdata = recv_msg(sock)

    # only used for the files that i dont have and are requesting chunks from 
    # a dictionary of files and the chunks w/chunk data
    global chunkdatalist
    if fileName in chunkdatalist.keys():
        chunkdatalist[fileName][int(chunk)] = newdata["data"]
    else:
        chunkdatalist = {fileName: {int(chunk): newdata["data"]}}    


    print("This is chunkdatalist: " + str(chunkdatalist))

    # writing to the file with chunks in order
    f = open(CLIENT_DIR+fileName, "w+")
    f.truncate(0)
    for chunk in sorted(chunkdatalist[fileName].keys()):
        f.write(chunkdatalist[fileName][chunk])
    f.close()

    # Tell the server that a peer got a new chunk
    data = message4(fileName, chunk)
    sock.close()
    return data

# message #5
def File_Chunk_Request(conn, addr):

    receive = conn.recv(4096).decode()
    data = json.loads(receive)
    # format a message to send back
    senddict = {}
    senddict["message"] = 5
    senddict["fileName"] = data["fileName"]
    senddict["chunk"] = data["chunk"]
    # find out what chunk of data to send from the file
    chunknum = data["chunk"]
    offset = (chunknum-1)*1024
    fileName = data["fileName"]
    f = open(CLIENT_DIR+fileName,"r")
    f.seek(offset)
    chunkfile = f.read(1024)
    senddict["data"] = chunkfile
    y = json.dumps(senddict)
    conn.sendto(str.encode(y),addr)
    return 0 
    # return -1 if failed

def recv_msg(sock):
    receive = sock.recv(4096).decode('utf-8')
    data = json.loads(receive)
    return data

def send_msg(sock, dic):
    send = json.dumps(dic)
    sock.send(str.encode(send))
    return 0

# for peer to peer connection
def start_listener(sock):
    sock.listen()
    while True:
        conn, addr = sock.accept()
        print("Connected by ", addr)
        start_new_thread(File_Chunk_Request, (conn, addr))


# localhost
HOST = '127.0.0.1'  
# Port to listen on 
# server port   
PORT = int(sys.argv[1])
# myself port
LISTEN_PORT = int(sys.argv[2])
CLIENT_DIR = "./"+sys.argv[3]+"/"
# a dictionary that has all the files and which ip address has what chunk
fileList = {}
# only used for the files that i dont have and are requesting chunks from 
# a dictionary of files and the chunks w/chunk data
chunkdatalist = {}

print("Waiting for connection")

# port to listen for peer to peer connection
sListen = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sListen.bind((HOST, LISTEN_PORT))
start_new_thread(start_listener, (sListen,))

while True:
    message = input("What message would you like to send: ").strip()
    
    message1()
    
    if message == "2":
        message2()

    if message == "3":
        message3()

    if message == "5":
        message5()
    
    # end loop
    if message == "6":
        break

