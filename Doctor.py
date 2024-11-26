from comunicacion import *
from modifyDB import modifyDB
from connectDB import *

def doctor():
    while True:
        print("1)Cerrar visita")
        print("2)Regresar")

        try:
            option = int(input("Ingrese una opción: "))
            if option == 1:
                cerrarVisita()
            elif option == 2:
                break
            else:
                raise ValueError()
        except:
            print("Ingrese una opción valida")

def cerrarVisita():
    modify = modify(connect_mysql())
    ipNodes = getNodes()
    doctores = modify.showBusyDoctor()
    folios = []

    try:
        while True:
            if not doctores:
                print("Doctores con consulta")
                i = 1
                for dato in doctores:
                    print(f"{i})Matricula: {dato[0]}\tNombre: {dato[1]} {dato[2]}")
                    folios.append(dato[3])
                    i += 1
                
                option = input("Ingrese cual visita dar de alta: ")
                option = int(option)
                if option > i:
                    print("Valor fuera de rango")
                else:
                    for ip in ipNodes:
                        cliente = ClientSocket()
                        if cliente.conect(ip, 65432):
                            cliente.send("ALTA", f"{folios[option-1]}")
                            _, _, tipo, mensaje = cliente.receive()
                            if tipo == "ALTA" and mensaje == "ok":
                                print("Actualizacion exitosa")
                            else:
                                print("Fallo a la hora de insertar dato")
                        else:
                            print(f"Nodo {ip} no disponible")

                    if modify.dischargePaciente(folios[option-1]):
                        print("Actualización exitosa")
                    else:
                        print("Fallo a la hora de insertar dato")
            else:
                print("No hay doctores con consulta en este momento")
                break
    except Error as e:
        print("Error", e)
