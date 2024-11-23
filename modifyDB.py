from mysql.connector import Error

class modifyDB:
    def __init__(self, connection=None):
        if conexion == None:
            print ("Error al cargar el cursor")
        else:
            self.connection
            self.cursor = connection.cursor()

    def insertDoctor(self, matricula, nombre, apellido, telefono):
        try:
            query = "INSERT INTO DOCTOR (matricula, nombre, apellido, telefono) VALUES (%s, %s, %s, %s)"
            value = (matricula, nombre, apellido, telefono)
            self.cursor.execute(query, value)
            self.connection.commit()
            return True
        except Error as e:
            print("Error a la hora de insertar datos", e)
            return False