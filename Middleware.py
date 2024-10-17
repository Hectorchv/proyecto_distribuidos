import socket
import threading
import time
from getIP import get_ipv4

def main():
    # Obtener la dirección IPv4 del host
    ipv4 = get_ipv4()

    # Iniciar servidor en un hilo
    server_thread = threading.Thread(target=start_server)
    server_thread.start()

    while True:
        print("\nMenú:")
        print("1) Enviar mensaje")
        print("2) Mostrar registro de mensaajes")
        print("3) Salir")

        option = input("Ingrese una opción: ")

        if option == '1':
            connect_to_remote_server()
        elif option == '2':
            print("\nRegistro de mensajes:")
            print_history()
        elif option == '3':
            server_thread
            return
        else:
            print("Ingrese una opción válida")

def start_server():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:

            server.bind(('', 65432))
            server.listen(5)
            print(f"Servidor iniciado")

            while True:
                conn, address = server.accept()
                connection_time = time.strftime('%Y-%m-%d %H:%M:%S')
                print(f"\nConección establecida con {address} a las {connection_time}")
                # Manejar la conexión del cliente en un hilo separado
                client_thread = threading.Thread(target=handle_client, args=(conn,))
                client_thread.start()
    except Exception as e:
        print("Error al iniciar el servidor:", e)


def connect_to_remote_server():
    try:
        # Leer las direcciones IP y puertos desde el archivo
        with open("remote_servers.txt", "r") as file:
            remote_servers = [line.strip().split() for line in file.readlines()]

        print("\nSeleccione el nodo:")
        for i, (ip, port) in enumerate(remote_servers, 1):
            print(f"{i}) {ip}")

        option = int(input("Seleccione una opción: "))
        if 1 <= option <= len(remote_servers):
            address, port = remote_servers[option - 1]
            port = int(port)

            # Crear un socket TCP/IP
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
                # Conectar el socket al servidor remoto
                client.connect((address, port))
                print("Conexión establecida con", address, "en el puerto", port)
                # Enviar mensajes al servidor remoto
                while True:
                    message = input("Ingrese mensaje ('exit' para salir): ")
                    if message.lower() == 'exit':
                        client.close()
                        break
                    message = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}"
                    client.sendall(message.encode())
                    # Guardar el mensaje enviado en el archivo de texto
                    save_message("localhost", message)
                    # Recibir la respuesta del servidor remoto
                    response = client.recv(1024)
                    print("Respuesta del nodo remoto:", response.decode())
        else:
            print("Ingrese una opción válida")
    except Exception as e:
        print("Connection refused:", e)


def handle_client(client):
    try:
        while True:
            # Recibir datos del cliente
            data = client.recv(1024)
            if not data:
                break
            # Imprimir el mensaje recibido del cliente
            print("Mensaje recibido del cliente:", data.decode())
            # Si el mensaje contiene un timestamp, imprímelo
            if '[' in data.decode() and ']' in data.decode():
                timestamp = data.decode().split('[')[1].split(']')[0]
                print("Timestamp del mensaje:", timestamp)
            # Guardar el mensaje recibido en el archivo de texto
            save_message(client.getpeername()[0], data.decode())
            # Si el cliente envía 'exit', salir del bucle y cerrar la conexión
            if data.decode().strip().lower() == 'exit':
                break
            # Enviar de vuelta el mensaje al cliente (eco)
            client.sendall("Mensaje recibido".encode())
    except Exception as e:
        print("Error al recivir mensaje", e)
    finally:
        # Cerrar el socket del cliente
        client.close()
        print("Conexión con el cliente cerrada.")

def save_message(ip_address, message):
    with open("messages.txt", "a") as file:
        file.write(f"IP: {ip_address}, Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}, Mensaje: {message}\n")


def print_history():
    try:
        with open("messages.txt", "r") as file:
            print(file.read())
    except FileNotFoundError:
        print("No se encontró ningún historial de mensajes.")

if __name__ == "__main__":
    main()
