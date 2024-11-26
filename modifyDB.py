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
            query = "INSERT INTO TRABAJADOR_SOCIAL (rfc, nombre, apellido, telefono) VALUES (%s, %s, %s, %s)"
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
            
    def insertVisita(self, paciente_id, doctor_id, cama_id):
        try:
            query = "INSERT INTO VISITA_EMERGENCIA (paciente_id, doctor_id, cama_id, fecha) VALUES (%s, %s, %s, %s)"
            value = (paciente_id, doctor_id, cama_id, datetime.now())
            self.cursor.execute(query,value)
            self.connection.commit()
            return True
        except Error as e:
            print("Error a la hora de insertar datos en la tabla VISITA_EMERGENCIA: ", e)
            return False
    
    def dischargePaciente(self, folio):
        try:
            query = "UPDATE VISITA_EMERGENCIA SET status = 1 WHERE folio = %s"
            value = folio
            self.cursor.execute(query, (value, ))
            self.connection.commit()
            return True
        except Error as e:
            print("Error a la hora de dar de alta al paciente: " , e)
            return False

    def consultVisit(self):
        try:
            query = '''
                SELECT
                    VISITA_EMERGENCIA.folio AS visita_id,
                    DOCTOR.matricula AS doctor_nombre,
                    PACIENTE.nSocial AS paciente_nombre
                FROM
                    VISITA_EMERGENCIA
                JOIN
                    DOCTOR ON VISITA_EMERGENCIA.doctor_id = DOCTOR.matricula
                JOIN
                    PACIENTE ON VISITA_EMERGENCIA.paciente_id = PACIENTE.nSocial
                WHERE
                    VISITA_EMERGENCIA.status = 0;
                    '''
            self.cursor.execute(query)
            return self.cursor.fetchall()

        except Error as e:
            print("Error consulta fallida: ", e)
            return None
    
    def consultAvailableCamas(self, sala):
        try:
            query = '''
                SELECT
                    CAMA_ATENCION.id AS cama_id
                FROM
                    CAMA_ATENCION
                LEFT JOIN
                    VISITA_EMERGENCIA
                ON
                    VISITA_EMERGENCIA.cama_id = CAMA_ATENCION.id
                WHERE
                    (VISITA_EMERGENCIA.status != 0 OR
                    VISITA_EMERGENCIA.status IS NULL) AND
                    CAMA_ATENCION.sala = %s
                    '''
            self.cursor.execute(query, (sala, ))
            return self.cursor.fetchall()
        except Error as e:
            print("Error en la culsulta: ",e)
            return None
    
    def consultAvailableDoctor(self):
        try:
            query = '''
                SELECT DISTINCT
                    DOCTOR.matricula as doctor_id
                FROM
                    DOCTOR
                LEFT JOIN
                    VISITA_EMERGENCIA
                ON 
                    DOCTOR.matricula = VISITA_EMERGENCIA.doctor_id
                WHERE
                    VISITA_EMERGENCIA.status != 0 OR VISITA_EMERGENCIA.status IS NULL;
                    '''
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Error as e:
            print("Error en la consulta: ", e)
            return None
    
    def consultPaciente(self, nSocial):
        try:
            query = '''
                SELECT
                    PACIENTE.nombre as paciente_nombre,
                    PACIENTE.apellido as paciente_apellido
                FROM
                    PACIENTE
                WHERE
                    PACIENTE.nSocial = %s;
                    '''
            self.cursor.execute(query, (nSocial,))
            return self.cursor.fetchall()
        except Error as e:
            print("Error en la consula ", e)
            return None
        
    def showAllDoctor(self):
        try:
            query = "SELECT * FROM DOCTOR;"
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Error as e:
            print("Error en la consuta ", e)
    
    def showAllCamas(self):
        try:
            query = "SELECT * FROM CAMA_ATENCION;"
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Error as e:
            print("Error en la consuta ", e)
    
    def showAllPaciente(self):
        try:
            query = "SELECT * FROM PACIENTE;"
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Error as e:
            print("Error en la consuta ", e)
    
    def showAllTrabajadores(self):
        try:
            query = "SELECT * FROM TRABAJADOR_SOCIAL;"
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Error as e:
            print("Error en la consuta ", e)

    def showBusyDoctor(self):
        try:
            query = '''
                SELECT DISTINCT
                    DOCTOR.matricula AS doctor_id,
                    DOCTOR.nombre AS doctor_nombre,
                    DOCTOR.apellido AS doctor_apellido,
                    VISITA_EMERGENCIA.folio as visita_folio
                FROM
                    DOCTOR
                INNER JOIN
                    VISITA_EMERGENCIA
                ON
                    VISITA_EMERGENCIA.doctor_id = DOCTOR.matricula
                WHERE
                    VISITA_EMERGENCIA.status = 0;
                    '''
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Error as e:
            print("Error en la consulta", e)
            return None
    
    def showBusyCamas(self, sala):
        try:
            query = '''
                SELECT DISTINCT
                    VISITA_EMERGENCIA.folio
                FROM
                    VISITA_EMERGENCIA
                INNER JOIN
                    CAMA_ATENCION
                ON
                    CAMA_ATENCION.id = VISITA_EMERGENCIA.cama.id
                WHERE
                    VISITA_EMERGENCIA.status = 0 AND CAMA_ATENCION.sala = %s;
                    '''
            self.cursor.execute(query, (sala,))
            return self.cursor.fetchall()

        except Error as e:
            print("Error en la consulta", e)
            return None

    def modifyVisita(self, folio, cama_id):
        try:
            query = '''
                UPDATE VISITA_EMERGENCIA
                SET cama_id = %s
                WHERE folio = %s;
                    '''
            self.cursor.execute(query, (cama_id, folio))
            self.connection.commit()
            return True
        except Error as e:
            print("Error al ejecutar la actualizacion ")
            return False
            
    def close(self):
        self.connection.close_connection()
