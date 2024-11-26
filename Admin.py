from comunicacion import *
from modifyDB import modifyDB
from connectDB import *

def admin():
    while True:
        print("1)Insertar doctor")
        print("2)Insertar cama")
        print("3)Insertar paciete")
        print("4)Insertar trabajador social")
        print("5)Ver todos los doctores")
        print("6)Ver todas las camas")
        print("7)Ver todos los pacientes")
        print("8)Ver todos los trabajadores sociales")
        print("9)Regresar")

        try:
            option = int(input("Ingrese una opción: "))
            if option == 1:
                insertarDoctor()
            elif option == 2:
                insertarCama()
            elif option == 3:
                nSocial = input("Ingrese el número de n social: ")
                insertarPaciente(nSocial)
            elif option == 4:
                insertarTrabajador()
            elif option == 5:
                verDoctores()
            elif option == 6:
                verCamas()
            elif option == 7:
                verPacientes()
            elif option == 8:
                verTrabajadores()
            elif option == 9:
                break
            else:
                raise ValueError()
        
        except Error as e:
            print("Ingrese una opción valida", e)

def insertarDoctor():

    matricula = input("Ingrese la matrícula: ")
    nombre = input("Ingrese el nombre: ")
    apellido = input("Ingrese el apellido: ")
    telefono = input("Ingrese el telefono: ")

    try:
        modify = modifyDB(connect_mysql())

        ipNodes = getNodes()
        print(ipNodes)

        for ip in ipNodes:
            cliente = ClientSocket()
            if cliente.conect(ip, 65432):
                cliente.send("INS_DOCTOR", f"{matricula} {nombre} {apellido} {telefono}")
                _, _, tipo, mensaje = cliente.receive()
                print()
                if tipo == "INS_DOCTOR" and mensaje == "ok":
                    print("Actualización exitosa")
                else:
                    print("Fallo a la hora de insertar dato")
            else:
                print(f"Nodo {ip} no disponible")

        if modify.insertDoctor(matricula, nombre, apellido, telefono):
            print("Actualizacion exitosa")
        else:
            print("Fallo al ingresar datos")

    except Error as E:
        print("Error ", e)

def insertarCama():
    modelo = input("Ingrese el modelo: ")
    marca = input("Ingrese la marca: ")
    sala = input("Ingrese la sala: ")

    try:
        modify =  modifyDB(connect_mysql())
        ipNodes = getNodes()

        for ip in ipNodes:
            cliente = ClientSocket()
            if cliente.conect(ip, 65432):
                cliente.send("INS_CAMA", f"{modelo} {marca} {sala}")
                _, _, tipo, mensaje = cliente.receive()
                if tipo == "INS_CAMA" and mensaje == "ok":
                    print("Actualización exitosa")
                else:
                    print("Fallo a la hora de insertar datos")
            else:
                print(f"Nodo {ip} no disponible")
        
        modify.insertCama(modelo, marca, sala)

    except Error as e:
        print("Error ", e)

def insertarPaciente(nSocial):
    nombre = input("Ingrese el nombre: ")
    apellido = input("Ingrese el apellido: ")
    telefono = input("Ingrese el telefono: ")

    try:
        modify = modifyDB(connect_mysql())

        ipNodes = getNodes()

        for ip in ipNodes:
            cliente = ClientSocket()
            if cliente.conect(ip, 65432):
                cliente.send("INS_PACIENTE", f"{nSocial} {nombre} {apellido} {telefono}")
                _, _, tipo, mensaje = cliente.receive()
                print()
                if tipo == "INS_PACIENTE" and mensaje == "ok":
                    print("Actualización exitosa")
                else:
                    print("Fallo a la hora de insertar dato")
            else:
                print(f"Nodo {ip} no disponible")

        modify.insertPaciente(nSocial, nombre, apellido, telefono)

    except Error as E:
        print("Error ", e)

def insertarTrabajador():

    rfc = input("Ingrese el rfc: ")
    nombre = input("Ingrese el nombre: ")
    apellido = input("Ingrese el apellido: ")
    telefono = input("Ingrese el telefono: ")

    try:
        modify = modifyDB(connect_mysql())
        ipNodes = getNodes()

        for ip in ipNodes:
            cliente = ClientSocket()
            if cliente.conect(ip, 65432):
                cliente.send("INS_TRABAJADOR", f"{rfc} {nombre} {apellido} {telefono}")
                _, _, tipo, mensaje = cliente.receive()
                print()
                if tipo == "INS_TRABAJADOR" and mensaje == "ok":
                    print("Actualización exitosa")
                else:
                    print("Fallo a la hora de insertar dato")
            else:
                print(f"Nodo {ip} no disponible")
            
        modify.insertTrabajador(rfc, nombre, apellido, telefono)

    except Error as E:
        print("Error ", e)

def verDoctores():
    try:
        modify = modifyDB(connect_mysql())
        doctores = modify.showAllDoctor()

        for dato in doctores:
            print("Matricula: ", dato[0])
            print("Nombre: ", dato[1])
            print("Apellido: ", dato[2])
            print("Telefono: ", dato[3])
            print("")
    except Error as e:
        print("Error", e)

def verCamas():
    try:
        modify = modifyDB(connect_mysql())
        camas = modify.showAllCamas()

        for dato in camas:
            print("Id: ", dato[0])
            print("Modelo: ", dato[1])
            print("Marca: ", dato[2])
            print("Sala: ", dato[3])
            print("")
    except Error as e:
        print("Error", e)

def verPacientes():
    try:
        modify = modifyDB(connect_mysql())
        pacientes = modify.showAllPaciente()

        for dato in pacientes:
            print("nSocial: ", dato[0])
            print("Nombre: ", dato[1])
            print("Apellido: ", dato[2])
            print("Telefono: ", dato[3])
            print("")
    except Error as e:
        print("Error", e)

def verTrabajadores():
    try:
        modify = modifyDB(connect_mysql())
        trabajador = modify.showAllTrabajadores()

        for dato in trabajador:
            print("rfc: ", dato[0])
            print("Nombre: ", dato[1])
            print("Apellido: ", dato[2])
            print("Telefono: ", dato[3])
            print("")
    except Error as e:
        print("Error", e)