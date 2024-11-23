import socket
import time
import threading
import sys
import re
from modifyDB import modifyDB
from connectDB import *
from getLocalIP import getLocalIP

MSGLEN = 1024
localIP = getLocalIP()
masterIP = "0.0.0.0"

def insertarDoctor(matricula, nombre, apellido, telefono):
    try:
        modify = modifyDB(connect_mysql())

        with open("nodes.txt", "r") as nodes:
            ipNodes  = [line.strip() for line in nodes.readlines()]
            ipNodes.remove(localIP)

        for ip in ipNodes:
            print(ip)
            cliente = ClientSocket()
            if cliente.conect(ip, 65432):
                cliente.send("INS_DOCTOR", f"{matricula} {nombre} {apellido} {telefono}")
                _, _, tipo, mensaje = cliente.receive()
                if tipo == "INS_DOCTOR " and mensaje == "ok":
                    print("Actualización exitosa")
                else:
                    print("Fallo a la hora de insertar dato")
            else:
                print(f"Nodo {ip} no disponible")

        modify.insertDoctor(matricula, nombre, apellido, telefono)

    except Error as E:
        print("Error ", e)
         
def electionMaster():
    global masterIP

    thisNodeIsMaster = True
    candidates = []

    with open("nodes.txt", "r") as nodes:
        ipNodes  = [line.strip() for line in nodes.readlines()]
        ipNodes.remove(localIP)

        for ip in ipNodes:
            if ip > localIP:
                candidates.append(ip)
    
    print(candidates)

    if candidates:
        for ip in candidates:
            cliente = ClientSocket()
            if cliente.conect(ip, 65432):
                cliente.send("ELECTION", "New election")
                ip, _, tipo, mensaje = cliente.receive()
                print(f"{mensaje} from: {ip}")
                if mensaje == "ok":
                    thisNodeIsMaster = False
            del cliente

    print(thisNodeIsMaster)

    if thisNodeIsMaster:
        for ip in ipNodes:
            cliente = ClientSocket()
            if cliente.conect(ip, 65432):
                cliente.send("COORDINATOR", "New coordinator")
                _, timestamp, tipo, mensaje = cliente.receive()
        
        masterIP = localIP

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

def handleClient(conn, addr):
    global masterIP
    modify = modifyDB(connect_mysql())

    servidor = comServer(conn,addr)

    #Maneja el tipo de mensaje
    ip, timestamp, tipo, mensaje = servidor.receive()
    if tipo == "MENSAJE":
        print(mensaje)
        servidor.send("MENSAJE", "OK")
    elif tipo == "ELECTION":
        servidor.send("OK", "ok")
        print("Nueva eleccion de nodo maestro")
        electionMaster()
    elif tipo == "COORDINATOR":
        print(f"Nuevo coordinador con IP: {ip}")
        masterIP = ip
        servidor.send("OK", "ok")
    elif tipo == "INS_DOCTOR":
        if modify.insertDoctor(mensaje.split()):
            servidor.send("INS_DOCTOR", "ok")
        else:
            servidor.send("INS_DOCTOR", "fail")

    register = open("register.txt", "a+")
    register.write(f"[{ip}][{timestamp}][{tipo}][{mensaje}]\n")
    register.close()

def miserver():

    servidor = ServerSocket()
    while True:
        conn, addr = servidor.accept()
        hilo = threading.Thread(target=handleClient, args=(conn,addr))
        hilo.start()
    

if __name__ == "__main__":

    #Server thread

    t1 = threading.Thread(target=miserver)
    t1.start()

    while True:

        ipNodes = []
        i = 1

        print("Enviar mensaje a:")
        with open("nodes.txt", "r") as nodes:
            ipNodes  = [line.strip() for line in nodes.readlines()]
        

        for ip in ipNodes:
            print(f"{i}) {ip}")
            i += 1
        
        print(f"{i}) Nuevo coordinador")
        print(f"{i+1}) Nodo maestro")
        print(f"{i+2}) Insertar doctor")
        
        while True:
            option = input("Ingrese una opcion: ")
            try:
                option = int(option)

                if option > len(ipNodes) + 3:
                    print("Valor fuera de rango")

                elif option == i:
                    electionMaster()
                elif option == i+1:
                    print(masterIP)
                elif option == i+2:
                    matricula = input("Ingrese la matrícula: ")
                    nombre = input("Ingrese el nombre: ")
                    apellido = input("Ingrese el apellido: ")
                    telefono = input("Ingrese el telefono: ")
                    insertarDoctor(matricula, nombre, apellido, telefono)

                else:
                    cliente = ClientSocket()

                    if cliente.conect(ipNodes[option - 1], 65432):
                        mensaje = input("Ingrese el mensaje: ")
                        cliente.send("MENSAJE", mensaje)
                        ip, timestamp, command, contenido = cliente.receive()

                        print(f"La respuesta de: {ip} con timestamp: {timestamp} de tipo: {command} es: {contenido}")
                    else:
                        print("No se logro conectar con el host")

                    break
            except ValueError:
                if option != "":
                    print("Ingrese una opcioin valida")

    t1.join()
    register.close()
    #t1.join()