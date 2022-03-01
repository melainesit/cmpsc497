
import socket
import threading
import os
from _thread import *
import json
import math
import sys

# message #1
# The server is being told what files the peer wants to share with the network
def register_request(conn, peer, files, lPort):
    peerKey = str(peer[0])+":"+str(lPort)
    for pFile in files:
        # checks if the file name exists in the dictinary 
        # if so, then add the list of chunks for that peer 
        if pFile[0] in fileDict:
            fileDict[pFile[0]][peerKey] = list(range(1, pFile[1]+1))
        
        # file name did not exist in the dictionary so add it in
        else:
            # add the peer and its chunks          
            fileDict[pFile[0]] = {peerKey: list(range(1, pFile[1]+1))}
        # send to peer that the specific file was successfully added to the server
        conn.sendto(str.encode(json.dumps({"message":1, "file":pFile[0], "success":1})), peer)
    return 0

# message #2: 
# requests the file list
# send the list length anf for each file, the file name and the length of that file to the peer
# takes in the peer ip address and port
def file_list_request(conn, peer):
    # format the message
    mydict = {}
    mydict["message"] = 2
    # number of files
    mydict["length"] = len(fileDict.keys())
    mydict["files"] = {}
    for key in fileDict:
        mydict["files"][key] = fileDict.get(key)
    y = json.dumps(mydict)
    conn.sendto(str.encode(y),peer)
    return 0

# message #3
# Requested: The IP end-points of the peers containting the requested file
def file_locations_request(conn, peer, filename):
    if filename in fileDict:
        # gets the peers and the chunks
        newdict = {
            "message": 3,
            "fileName" : filename,
            "peers": fileDict.get(filename)
        }
        # the number of endpoints
        newdict["length"] = len(fileDict.get(filename).keys())
        y = json.dumps(newdict)
        conn.sendto(str.encode(y),peer)
        return 0
    else:
        return -1
    # else none if the filename doesnt exist?

# message #4
# The server is being notified when a peer receives a new chunk of the file and becomes a source 
# (of that chunk) for other peers
def chunk_register_request(conn, peer, pFile, chunk, lPort):
    peerKey = str(peer[0])+":"+str(lPort)
    if peerKey in fileDict[pFile].keys():
        fileDict[pFile][peerKey].append(chunk)
        fileDict[pFile][peerKey] = list(set(fileDict[pFile][peerKey]))
    else: 
        fileDict[pFile][peerKey] = [chunk]
    conn.sendto(str.encode(json.dumps({"message":4, "file":pFile, "chunk":chunk, "success":1})), peer)
    return 0


# handles requests from the individual client within a thread
def handle_conn(conn, peer):
    data = conn.recv(4096).decode()
    data = json.loads(data)
    message = data["message"]
    print(data)
    if message == 1:
        files = []
        for pFile in data["files"]:
            #  each chunk is 1024 bytes
            files.append((pFile[0], math.ceil(pFile[1] / 1024)))
        register_request(conn, peer, files, data["lPort"])
    
    if message == 2:
        file_list_request(conn, peer)
    
    if message == 3:
        filename = data["fileName"]
        file_locations_request(conn, peer, filename)
        
    if message == 4:
        lPort = data["lPort"]
        pFile = data["fileName"]
        chunk = data["chunk"]
        chunk_register_request(conn, peer, pFile, chunk, lPort)
    conn.close()
    
# a dictionary where the key is the file name. Each file name has a dictionary. in that dictionary it will have the peer as a key 
# and a list of chunks it has. the peer will be a tuple of ip addr and port
# ex: {filename: {peer1: [1,3,5,7,8]}}
fileDict = {}

# localhost
HOST = '127.0.0.1'  
# Port to listen on    
PORT = int(sys.argv[1])
    
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((HOST,PORT))
print("Waiting for a connection")
sock.listen()

while True:
    conn, addr = sock.accept()
    print("Connected by ", addr)
    start_new_thread(handle_conn, (conn, addr))
sock.close()
