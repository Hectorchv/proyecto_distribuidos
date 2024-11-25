from mysql.connector import Error
from datetime import datetime

class modifyDB:
    def __init__(self, connection=None):
        if connection == None:
            print ("Error al cargar el cursor")
        else:
            self.connection = connection
            self.cursor = connection.cursor()

    def insertDoctor(self, matricula, nombre, apellido, telefono):
        try:
            query = "INSERT INTO DOCTOR (matricula, nombre, apellido, telefono) VALUES (%s, %s, %s, %s)"
            value = (matricula, nombre, apellido, telefono)
            self.cursor.execute(query, value)
            self.connection.commit()
            return True
        except Error as e:
            print("Error a la hora de insertar datos en la tabla DOCTOR", e)
            return False
    
    def insertPaciente(self, nSocial, nombre, apellido, telefono):
        try:
            query = "INSERT INTO PACIENTE (nSocial, nombre, apellido, telefono) VALUES (%s, %s, %s, %s)"
            value = (nSocial, nombre, apellido, telefono)
            self.cursor.execute(query, value)
            self.connection.commit()
            return True
        except Error as e:
            print("Error a la hora de insertar datos en la tabla PACIENTE: ", e)
            return False
    
    def insertTrabajador(self, rfc, nombre, apellido, telefono):
        try:
            query = "INSERT INTO PACIENTE (rfc, nombre, apellido, telefono) VALUES (%s, %s, %s, %s)"
            value = (rfc, nombre, apellido, telefono)
            self.cursor.execute(query,value)
            self.connection.commit()
            return True
        except Error as e:
            print("Error a la hora de insertar datos en la tabla TRABAJADOR_SOCIAL: ", e)
            return False

    def insertCama(self, modelo, marca, sala):
        try:
            query = "INSERT INTO CAMA_ATENCION (modelo, marca, sala) VALUES (%s, %s, %s)"
            value = (modelo, marca, sala)
            self.cursor.execute(query,value)
            self.connection.commit()
            return True
        except:
            print("Error a la hora de insertar datos en la tabla CAMA_ATENCION: ", e)
            return False
            
    def insertVisita(self, folio, paciente_id, doctor_id, cama_id):
        try:
            query = "INSERT INTO VISITA_EMERGENCIA (folio, paciente_id, doctor_id, cama_id, fecha) VALUES (%s, %s, %s, %s, %s)"
            value = (folio, paciente_id, doctor_id, cama_id, datetime.now())
            self.cursor.execute(query,value)
            self.connection.commit()
            return True
        except:
            print("Error a la hora de insertar datos en la tabla VISITA_EMERGENCIA: ", e)
            return False
