from socket import socket, AF_INET, SOCK_STREAM
import os
import mimetypes
from datetime import datetime

HOST = 'localhost'
PORT = 8080
BASE_DIR = './www'
s = socket(AF_INET, SOCK_STREAM) 
s.bind((HOST, PORT))
s.listen(1)
print(f"Server in ascolto su http://{HOST}:{PORT}")

def LogRequest(addr, method, path, statusCode):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logEntry = f"[{now}] {addr} {method} {path} -> {statusCode}"
    print(logEntry)
    with open("log.txt", "a") as logFile:
        logFile.write(logEntry + "\n")

def HandleRequest(connection, addr):
    request = connection.recv(1024).decode()
    if not request:
        connection.close()
        return

    lines = request.split('\r\n')
    method, path, _ = lines[0].split()

    if method != 'GET':
        connection.close()
        return

    if path == '/' or path == '':
        path = '/index.html'
    filePath = os.path.abspath(BASE_DIR + path)

    if os.path.isfile(filePath):
        f = open(filePath, 'rb')
        content = f.read()
        mimeType, _ = mimetypes.guess_type(filePath)
        mimeType = mimeType or 'application/octet-stream'
        header = (
            "HTTP/1.1 200 OK\r\n"
            f"Content-Type: {mimeType}\r\n"
            f"Content-Length: {len(content)}\r\n"
            "Connection: close\r\n"
            "\r\n"
        )
        connection.sendall(header.encode() + content)
        LogRequest(addr, method, path, 200)
    else:
        response = (
            "HTTP/1.1 404 Not Found\r\n"
            "Content-Type: text/html\r\n"
            "\r\n"
            "<h1>404 Not Found</h1>"
        )
        connection.sendall(response.encode())
        LogRequest(addr, method, path, 404)

    connection.close()

while True:
    connection, addr = s.accept()
    HandleRequest(connection, addr)
    