import socket
import sys
import subprocess
import os

def main():
    if len(sys.argv) != 2:
        print("Usage: python serv.py <port>")
        sys.exit(1)
    
    # get port from command line
    port = int(sys.argv[1])
    
    # make the main server socket
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.bind(('', port))
    serverSocket.listen(1)
    
    print(f"Server listening on port {port}")
    
    #keep waiting for clients forever
    while True:
        connSocket, addr = serverSocket.accept()
        print(f"Client connected from {addr}")
        
        while True:
            command = connSocket.recv(1024).decode()
            
            if not command:
                break
                
            # split command text into parts
            parts = command.split()
            cmd = parts[0]
            
            if cmd == 'get':
                # client wants to download a file
                filename = parts[1]
                dataPort = int(parts[2])
                
                if not os.path.exists(filename):
                    connSocket.send("FAILURE".encode())
                else:
                    #read
                    with open(filename, 'rb') as f:
                        fileData = f.read()
                    
                    # connect to client's data port
                    dataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    dataSocket.connect((addr[0], dataPort))
                    
                    fileSize = len(fileData)
                    dataSocket.send(f"{fileSize:<10}".encode())
                    
                    bytesSent = 0
                    while bytesSent != fileSize:
                        bytesSent += dataSocket.send(fileData[bytesSent:])
                    
                    dataSocket.close()
                    connSocket.send("SUCCESS".encode())

            elif cmd == 'put':
                # client wants to upload a file
                filename = parts[1]
                dataPort = int(parts[2])
                
                # connect to client data port
                dataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                dataSocket.connect((addr[0], dataPort))
                
                fileSize = int(dataSocket.recv(10).decode().strip())
                
                # read file bytes until full size
                fileData = b""
                while len(fileData) != fileSize:
                    chunk = dataSocket.recv(4096)
                    if not chunk:
                        break
                    fileData += chunk
                
                # close data socket
                dataSocket.close()
                
                with open(filename, 'wb') as f:
                    f.write(fileData)
                
                connSocket.send("SUCCESS".encode())

            elif cmd == 'ls':
                dataPort = int(parts[1])
                
                result = subprocess.run(['ls'], capture_output=True, text=True)
                lsOutput = result.stdout.encode()
                
                dataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                dataSocket.connect((addr[0], dataPort))
                
                # send output size first
                fileSize = len(lsOutput)
                dataSocket.send(f"{fileSize:<10}".encode())
                
                bytesSent = 0
                while bytesSent != fileSize:
                    bytesSent += dataSocket.send(lsOutput[bytesSent:])
                
                dataSocket.close()
                connSocket.send("SUCCESS".encode())

            elif cmd == 'quit':
                # close this connection
                print("Client disconnected")
                connSocket.close()
                break

main()
