def doctor():
    while True:
        print("1)Cerrar visita")
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