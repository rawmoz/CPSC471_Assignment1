import socket
import sys

def main():
    #step 1: validate command arguments
    if len(sys.argv) != 3:
        print("Usage: python cli.py <server> <port>")
        sys.exit(1)
    
    #step 2: read server info from the command line
    serverName = sys.argv[1]
    serverPort = int(sys.argv[2])
    
    #step 3: open the control connection to the server
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.connect((serverName, serverPort))
    
    #step 4: keep acepting user commands until quit
    while True:
        command = input("ftp> ")
        
        if not command:
            continue
        
        parts = command.split()
        cmd = parts[0]
        
        if cmd == 'get':
            # GET command
            filename = parts[1]
            
            # open a temporary data socket and telling what server which port to use
            dataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            dataSocket.bind(('', 0))
            dataPort = dataSocket.getsockname()[1]
            dataSocket.listen(1)
            
            clientSocket.send(f"get {filename} {dataPort}".encode())
            
            dataConn, _ = dataSocket.accept()
            
            fileSize = int(dataConn.recv(10).decode().strip())
            
            fileData = b""
            while len(fileData) != fileSize:
                chunk = dataConn.recv(4096)
                if not chunk:
                    break
                fileData += chunk
            
            dataConn.close()
            dataSocket.close()
            
            with open(filename, 'wb') as f:
                f.write(fileData)
            
            # read and print final server status
            status = clientSocket.recv(1024).decode()
            print(status)
            print(f"{filename}: {fileSize} bytes transferred")

        elif cmd == 'put':
            # PUT command
            filename = parts[1]
            
            # read file contents from disk first
            with open(filename, 'rb') as f:
                fileData = f.read()
            
            dataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            dataSocket.bind(('', 0))
            dataPort = dataSocket.getsockname()[1]
            dataSocket.listen(1)
            
            clientSocket.send(f"put {filename} {dataPort}".encode())
            
            # accept incoming data connection from server
            dataConn, _ = dataSocket.accept()
            
            # send fixedwidth file size header then stream bytes
            fileSize = len(fileData)
            dataConn.send(f"{fileSize:<10}".encode())
            
            bytesSent = 0
            while bytesSent != fileSize:
                bytesSent += dataConn.send(fileData[bytesSent:])
            
            dataConn.close()
            dataSocket.close()
            
            # read and print final server status
            status = clientSocket.recv(1024).decode()
            print(status)
            print(f"{filename}: {fileSize} bytes transferred")

        elif cmd == 'ls':
            #ls
            dataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            dataSocket.bind(('', 0))
            dataPort = dataSocket.getsockname()[1]
            dataSocket.listen(1)
            
            clientSocket.send(f"ls {dataPort}".encode())
            
            # accept incoming data connection from server
            dataConn, _ = dataSocket.accept()
            
            fileSize = int(dataConn.recv(10).decode().strip())
            
            # receive directory listing bytes
            data = b""
            while len(data) != fileSize:
                chunk = dataConn.recv(4096)
                if not chunk:
                    break
                data += chunk
            
            # close data connection and print listing
            dataConn.close()
            dataSocket.close()
            
            print(data.decode())
            
            status = clientSocket.recv(1024).decode()
            print(status)

        elif cmd == 'quit':
            clientSocket.send("quit".encode())
            clientSocket.close()
            print("Bye!")
            break
        else:
            print("Unknown command")

main()
