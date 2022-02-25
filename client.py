
import socket

# localhost
HOST = '127.0.0.1'  
# Port to listen on    
PORT = 65007

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
s.connect((HOST,PORT))
    #s.sendall(b'Hello world')
data = s.recv(1024)

#print('Receiveed', str(data))

while True:
    line = input("Send the Server message:")
    if line == 'exit':
        break

    s.send(str.encode(line))
    data = s.recv(1024)

    print(data.decode('utf-8'))

s.close()