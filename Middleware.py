import time
import random
from Admin import admin
from Doctor import doctor
from Trabajador import tSocial
from comunicacion import *
from modifyDB import modifyDB
from connectDB import *
from getLocalIP import getLocalIP

MSGLEN = 1024
localIP = getLocalIP()
masterIP = "0.0.0.0"

def generarVisita(paciente_id):
    modify = modifyDB(connect_mysql())

    doctores =  modify.consultAvailableDoctor()
    print(doctores)

    num = 0
    sala = 0
    camas = None
    for i in range(1,5):
        prueba = modify.consultAvailableCamas(i)
        print(prueba)
        if len(prueba) > num:
            camas = prueba
            sala = i
    
    if not doctores:
        print("Sin doctores disponible")
        return False
    if not camas:
        print("Sin camas disponibles")
        return False

    doctor_id = random.choice(doctores)[0]
    cama_id = random.choice(camas)[0]

    ipNodes = getNodes()
    
    print(f"Generando visita para {paciente_id} doctor {doctor_id} cama {cama_id} en la sala {sala}")
    for ip in ipNodes:
        cliente = ClientSocket()
        if cliente.conect(ip, 65432):
            cliente.send("INS_VISITA", f"{paciente_id} {doctor_id} {cama_id}")
            _, _, tipo, mensaje = cliente.receive()
            print()
            if tipo == "INS_VISITA" and mensaje == "ok":
                print("Actualización exitosa")
            else:
                print("Fallo a la hora de insertar dato")
        else:
            print(f"Nodo {ip} no disponible")
        
    modify.insertVisita(paciente_id, doctor_id, cama_id)
    return True

def electionMaster():
    global masterIP

    thisNodeIsMaster = True
    candidates = []

    ipNodes = getNodes()

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


#Maneja a cada uno de los clientes y reacciona segun el tipo de mensaje
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
        matricula, nombre, apellido, telefono = mensaje.split()
        if modify.insertDoctor(matricula,mensaje,apellido,telefono):
            servidor.send("INS_DOCTOR", "ok")
        else:
            servidor.send("INS_DOCTOR", "fail")
    elif tipo == "INS_PACIENTE":
        nSocial, nombre, apellido, telefono = mensaje.split()
        if modify.insertPaciente(nSocial,mensaje,apellido,telefono):
            servidor.send("INS_PACIENTE", "ok")
        else:
            servidor.send("INS_PACIENTE", "fail")
    elif tipo == "INS_TRABAJADOR":
        rfc, nombre, apellido, telefono = mensaje.split()
        if modify.insertTrabajador(rfc,mensaje,apellido,telefono):
            servidor.send("INS_PACIENTE", "ok")
        else:
            servidor.send("INS_PACIENTE", "fail")
    elif tipo == "INS_CAMA":
        modelo, marca, sala = mensaje.strip()
        if modify.insertCama(modelo, marca, sala):
            servidor.send("INS_CAMA", "ok")
        else:
            servidor.send("INS_CAMA", "fail")
    elif tipo == "INS_VISITA":
        paciente_id, doctor_id, cama_id = mensaje.strip()
        if modify.insertVisita(paciente_id, doctor_id, cama_id):
            servidor.send("INS_VISITA", "ok")
        else:
            servidor.send("INS_VISITA", "fail")
    elif tipo == "VISITA":
        nSocial =  mensaje
        if generarVisita(nSocial):
            servidor.send("VISITA", "ok")
        else:
            servidor.send("VISITA", "fail")
    else:
        servidor.send("FAIL", "comando no valido")

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

    t1 = threading.Thread(target=miserver, daemon=True)
    t1.start()

    while True:
        print("1)Ingresar como administrador")
        print("2)Ingresar como trabajador social")
        print("3)Ingresar como doctor")
        print("4)Election")
        print("5)Salir")

        option = input("Ingrese una opción: ")
        try:
            option = int(option)
            if option == 1:
                admin()
            elif option == 2:
                tSocial()
            elif option == 3:
                doctor()
            elif option == 4:
                electionMaster()
            elif option == 5:
                break
            else:
                print("Ingrese un valor dentro del rango")
        except ValueError as e:
            print("Ingrese una opción valida", e)

    """

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
        print(f"{i+3}) Insertar paciente")
        while True:
            option = input("Ingrese una opcion: ")
            try:
                option = int(option)

                if option > len(ipNodes) + 4:
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
                elif option == i+3:
                    nSocial = input("Ingrese n social: ")
                    nombre = input("Ingrese el nombre: ")
                    apellido = input("Ingrese el apellido: ")
                    telefono = input("Ingrese el telefono: ")
                    insertarPaciente(nSocial, nombre, apellido, telefono)
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

    """
    t1.join()
    register.close()
