from mysql.connector import Error

class modifyDB:
    def __init__(self, cursor=None):
        if cursor == None:
            print ("Error al cargar el cursor")
        else:
            self.cursor = cursor

    def insertDoctor(self, matricula, nombre, apellido, telefono):
        try:
            query = "INSERT INTO DOCTOR (matricula, nombre, apellido, telefono) VALUES (%s, %s, %s, %s)"
            value = (matricula, nombre, apellido, telefono)
            self.cursor.execute(query, value)
            self.cursor.commit()
            return True
        except Error:
            print("Error a la hora de insertar datos", Error)
            return False