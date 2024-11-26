import socket
import time
import threading
import sys
import re

from getLocalIP import getLocalIP
MSGLEN = 1024
localIP = getLocalIP()
masterIP = "0.0.0.0"

def getNodes():
    try:
        with open("nodes.txt", "r") as nodes:
            ipNodes  = [line.strip() for line in nodes.readlines()]
            ipNodes.remove(localIP)
        return ipNodes
    except Error as e:
        print("Error a la hora de cargar los nodos: ", e)
        return None

class ClientSocket:
    def __init__(self, sock=None):
        if sock is None:
            try:
                self.sock = socket.socket(
                    socket.AF_INET, socket.SOCK_STREAM)
            except socket.error as err:
                print("Socket creation failed with error: %s", err)
        
        else:
            self.sock = sock
    
    def conect(self, host, port):
        try:
            self.addr = host
            self.port = port
            self.sock.connect((host, port))
            return True
        except ConnectionRefusedError :
            print(f"Conection refused by ({host}, {port})")
            self.sock.close()
            return False
        except OSError as e:
            if e.errno == 113:
                print(f"Ruta a {self.addr} no encontrada: ", e)
            else:
                print(e)
            return False


    def send(self, command, msg):
        totalsent = 0
        timestamp = time.time()
        timestamp = time.ctime(timestamp)
        msg = f"[{timestamp}][{command}][{msg}]"
        msglen = len(msg)
        msg = msg.encode()
        
        while totalsent < msglen:
            sent = self.sock.send(msg[totalsent:])
            if sent == 0:
                raise RuntimeError("Socket connection broken")
            totalsent = totalsent + sent
        self.sock.shutdown(socket.SHUT_WR)
    
    def receive(self):
        chunks = []
        bytes_recd = 0
        while bytes_recd < MSGLEN:
            chunk =  self.sock.recv(min(MSGLEN - bytes_recd, 2048))
            if chunk == b'':
                break
            chunks.append(chunk.decode())
            bytes_recd = bytes_recd + len(chunk)

        mensaje = f"[{self.addr}]" + "".join(chunks)
        elementos =  re.findall(r'\[(.*?)\]', mensaje)
        return elementos[0], elementos[1], elementos[2], elementos[3]

class ServerSocket:
    def __init__(self, sock=None, host='', port=65432):
        if sock is None:
            try:
                self.sock = socket.socket(
                    socket.AF_INET, socket.SOCK_STREAM)
            except socket.error as err:
                print("Socket creation failed with error: %s", err)
        else:
            self.sock = sock

        self.sock.bind(('', 65432))
        self.sock.listen(5)
    
    def accept(self):
        conn, addr = self.sock.accept()
        print(f"\nConnected by : {addr}")
        return conn, addr

class comServer:
    def __init__(self, conn, addr):
        self.conn = conn
        self.addr = addr

    def send(self, command, msg):
        totalsent = 0
        timestamp = time.time()
        timestamp = time.ctime(timestamp)
        msg = f"[{timestamp}][{command}][{msg}]"
        msglen = len(msg)
        msg = msg.encode()

        while totalsent < msglen:
            sent = self.conn.send(msg[totalsent:])
            if sent == 0:
                raise RuntimeError("Socket connection broken")
            totalsent = totalsent + sent
        self.conn.close()
    
    def receive(self):
        chunks = []
        bytes_recd = 0
        while bytes_recd < MSGLEN:
            chunk =  self.conn.recv(min(MSGLEN - bytes_recd, 2048))
            if chunk == b'':
                break
            chunks.append(chunk.decode())
            bytes_recd = bytes_recd + len(chunk)

        mensaje = f"[{self.addr[0]}]" + "".join(chunks)
        elementos =  re.findall(r'\[(.*?)\]', mensaje)
        return elementos[0], elementos[1], elementos[2], elementos[3]