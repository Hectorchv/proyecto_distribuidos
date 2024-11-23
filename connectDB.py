import mysql.connector
from mysql.connector import Error

def connect_mysql():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='admin',
            password='distribuidos123',
            database='hospital',
        )

        if connection.is_connected():
            print("Conexión exitosa con la base de datos")
            return connection
        else:
            print("Error al conectar a la base de datos")
            return None
    
    except Error as e:
        print("Error al concentar a MySQL: ", e)
        return None

def close_connection(connection):
    connection.close()

if __name__ == "__main__":
    connect_mysql()