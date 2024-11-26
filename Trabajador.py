from comunicacion import *
from modifyDB import modifyDB
from connectDB import *
from Admin import insertarPaciente

def tSocial():
    while True:
        print("1)Agendar visita")
        print("2)Regresar")

        try:
            option = int(input("Ingrese una opción: "))
            if option == 1:
                pass
            elif option == 2:
                break
            else:
                raise ValueError()
        except:
            print("Ingrese una opción valida")
        
def agendarVisita():
    try:
        modify = modifyDB(connect_mysql())

        while True:
            nSocial = input("Ingrese el número de seguro social: ")

            datos = modify.consultPaciente(nSocial)

            if datos:
                print(f"Generando consulta para el paciente {datos[0]} {datos[1]}")
                break
            else:
                print("Generando paciente nuevo")
                insertarPaciente(nSocial)

        cliente = ClientSocket()
        if cliente.conect(masterIP, 65432):
            cliente.send("VISITA", nSocial)
            _, _, tipo, mensaje= cliente.receive()
            if tipo == "VISITA":
                print(mensaje)
    except:
        print("Error al generar la visita")