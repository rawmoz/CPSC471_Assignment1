import socket
import sys

def main():
    if len(sys.argv) != 3:
        print("Usage: python cli.py <server> <port>")
        sys.exit(1)
    
    serverName = sys.argv[1]
    serverPort = int(sys.argv[2])
    
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.connect((serverName, serverPort))
    
    while True:
        command = input("ftp> ")
        
        if not command:
            continue
        
        parts = command.split()
        cmd = parts[0]
        
        if cmd == 'get':
            filename = parts[1]
            
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
            
            status = clientSocket.recv(1024).decode()
            print(status)
            print(f"{filename}: {fileSize} bytes transferred")

        elif cmd == 'put':
            filename = parts[1]
            
            with open(filename, 'rb') as f:
                fileData = f.read()
            
            dataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            dataSocket.bind(('', 0))
            dataPort = dataSocket.getsockname()[1]
            dataSocket.listen(1)
            
            clientSocket.send(f"put {filename} {dataPort}".encode())
            
            dataConn, _ = dataSocket.accept()
            
            fileSize = len(fileData)
            dataConn.send(f"{fileSize:<10}".encode())
            
            bytesSent = 0
            while bytesSent != fileSize:
                bytesSent += dataConn.send(fileData[bytesSent:])
            
            dataConn.close()
            dataSocket.close()
            
            status = clientSocket.recv(1024).decode()
            print(status)
            print(f"{filename}: {fileSize} bytes transferred")

        elif cmd == 'ls':
            dataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            dataSocket.bind(('', 0))
            dataPort = dataSocket.getsockname()[1]
            dataSocket.listen(1)
            
            clientSocket.send(f"ls {dataPort}".encode())
            
            dataConn, _ = dataSocket.accept()
            
            fileSize = int(dataConn.recv(10).decode().strip())
            
            data = b""
            while len(data) != fileSize:
                chunk = dataConn.recv(4096)
                if not chunk:
                    break
                data += chunk
            
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