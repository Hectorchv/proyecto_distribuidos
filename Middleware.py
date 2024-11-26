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
            num = len(prueba)
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

def redistribuirCarga(nodosMuertos):
    if nodosMuertos:
        modify = modifyDB(connect_mysql())
        ipNodes = getNodes()

        try:
            with open("nodes.txt", "r") as nodes:
                salas  = [line.strip() for line in nodes.readlines()]
        except Error as e:
            print("Error a la hora de cargar los nodos: ", e)
        
        indices = []
        for i in nodosMuertos:
            indices.append(salas.index(i)+1)
        disponibles = [1,2,3,4]
        for i in indices:
            disponibles.remove(i)

        for i in indices:
            citas = modify.showBusyCamas(i)
            if citas:
                print(f"Distribuyendo citas de la sala {i} caida")
                for folio in citas:
                    num = 0
                    for i in disponibles:
                        prueba = modify.consultAvailableCamas(i)
                        if len(prueba) > num:
                            camas = prueba
                            num = len(prueba)
                            sala = i
                    
                    if camas:
                        cama_id = random.choice(camas)[0]
                        print(f"Distribuyendo cita {folio[0]} a la sala {sala} i a la cama {cama_id}")
                        
                        for ip in ipNodes:
                            cliente = ClientSocket()
                            if cliente.conect(ip, 65432):
                                cliente.send("CAMBIAR_CAMA", f"{folio[0]} {cama_id}")
                                _, _, tipo, mensaje = cliente.receive()
                                print()
                                if tipo == "CAMBIAR_CAMA" and mensaje == "ok":
                                    print("Actualización exitosa")
                                else:
                                    print("Fallo a la hora de insertar dato")

                        modify.modifyVisita(folio[0], cama_id)
                    else:
                        print("No hay camas disponibles")
            else:
                print(f"Sin citas en la sala {i}")

def heartBit():
    while True:
        time.sleep(5)
        nodosMuertos = []
        if masterIP == localIP:
            ipNodes = getNodes()

            for ip in ipNodes:
                cliente = ClientSocket()
                if cliente.conect(ip, 65432):
                    cliente.send("HEARTBIT", "ok")
                    _, _, tipo, mensaje = cliente.receive()
                    if tipo == "HEARTBIT" and mensaje != "ok":
                        print(f"Nodo {ip} muerto")
                else:
                    print(f"Nodo {ip} muerto")
                    nodosMuertos.append(ip)
            if nodosMuertos:
                redistribuirCarga(nodosMuertos)
        else:
            cliente = ClientSocket()
            if cliente.conect(masterIP, 65432):
                cliente.send("HEARTBIT", "ok")
                _, _, tipo, mensaje = cliente.receive()
                if tipo == "HEARTBIT" and mensaje != "ok":
                    print(f"Nodo {ip} muerto")
            else:
                print("Nodo maestro muerto")
                electionMaster()         
        

def electionMaster():
    global masterIP

    thisNodeIsMaster = True
    candidates = []

    ipNodes = getNodes()

    for ip in ipNodes:
        if ip > localIP:
            candidates.append(ip)

    if candidates:
        for ip in candidates:
            cliente = ClientSocket()
            if cliente.conect(ip, 65432):
                cliente.send("ELECTION", "New election")
                ip, _, tipo, mensaje = cliente.receive()
                #print(f"{mensaje} from: {ip}")
                if mensaje == "ok":
                    thisNodeIsMaster = False
            del cliente

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
        electionMaster()
    elif tipo == "COORDINATOR":
        masterIP = ip
        servidor.send("OK", "ok")
    elif tipo == "INS_DOCTOR":
        matricula, nombre, apellido, telefono = mensaje.split()
        if modify.insertDoctor(matricula,nombre,apellido,telefono):
            servidor.send("INS_DOCTOR", "ok")
        else:
            servidor.send("INS_DOCTOR", "fail")
    elif tipo == "INS_PACIENTE":
        nSocial, nombre, apellido, telefono = mensaje.split()
        if modify.insertPaciente(nSocial,nombre,apellido,telefono):
            servidor.send("INS_PACIENTE", "ok")
        else:
            servidor.send("INS_PACIENTE", "fail")
    elif tipo == "INS_TRABAJADOR":
        rfc, nombre, apellido, telefono = mensaje.split()
        if modify.insertTrabajador(rfc,nombre,apellido,telefono):
            servidor.send("INS_TRABAJADOR", "ok")
        else:
            servidor.send("INS_TRABAJADOR", "fail")
    elif tipo == "INS_CAMA":
        modelo, marca, sala = mensaje.split()
        if modify.insertCama(modelo, marca, sala):
            servidor.send("INS_CAMA", "ok")
        else:
            servidor.send("INS_CAMA", "fail")
    elif tipo == "INS_VISITA":
        paciente_id, doctor_id, cama_id = mensaje.split()
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
    elif tipo == "ALTA":
        folio, folio_gen = mensaje
        with open("Folios.txt", "a+") as archivo:
            archivo.write(folio_gen, "\n")
        archivo.close()
        if modify.dischargePaciente(folio):
            servidor.send("ALTA", "ok")
        else:
            servidor.send("ALTA", "fail")
    elif tipo == "HEARTBIT":
        servidor.send("HEARTBIT","ok")
    elif tipo == "CAMBIAR_CAMA":
        folio, cama_id = mensaje.split()
        if modify.modifyVisita(folio, cama_id):
            servidor.send("CAMBIAR_CAMA", "ok")
        else:
            servidor.send("CAMBIAR_CAMA", "fail")
    else:
        servidor.send("FAIL", "comando no valido")
    
    modify.close()
    del modify

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

    electionMaster()
    
    t2 = threading.Thread(target=heartBit, daemon=True)
    t2.start()

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

    t1.join()
    register.close()
