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
        except Error as e:
            print("Ingrese una opción valida ", e)

def cerrarVisita():
    modify = modifyDB(connect_mysql())
    ipNodes = getNodes()
    doctores = modify.showBusyDoctor()
    folios = []

    try:
        while True:
            if doctores:
                print("Doctores con consulta")
                i = 0
                for dato in doctores:
                    i += 1
                    print(f"{i})Matricula: {dato[0]}\tNombre: {dato[1]} {dato[2]}")
                    folios.append(dato[3])
                    
                
                option = input("Ingrese cual visita dar de alta: ")
                option = int(option)
                if option > i:
                    print("Valor fuera de rango")
                else:
                    datos = modify.showAllVisita(folios[option-1])[0]
                    sala = modify.showSala(datos[3])[0]
                    folio_gen = f"{datos[1]}{datos[2]}{sala[0]}{datos[0]}"
                    for ip in ipNodes:
                        cliente = ClientSocket()
                        if cliente.conect(ip, 65432):
                            cliente.send("ALTA", f"{folios[option-1]} {folio_gen}")
                            _, _, tipo, mensaje = cliente.receive()
                            if tipo == "ALTA" and mensaje == "ok":
                                print("Actualizacion exitosa")
                            else:
                                print("Fallo a la hora de insertar dato")
                        else:
                            print(f"Nodo {ip} no disponible")

                    if modify.dischargePaciente(folios[option-1]):
                        print("Actualización exitosa")
                        print("Folio: ", folio_gen)
                        with open("Folios.txt", "a+") as archivo:
                            archivo.write(f"{folio_gen}\n")
                        archivo.close()
                    else:
                        print("Fallo a la hora de insertar dato")
                    break
            else:
                print("No hay doctores con consulta en este momento")
                break
    except Error as e:
        print("Error", e)
