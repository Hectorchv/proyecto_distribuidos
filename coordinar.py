import socket
import threading
import time
from getIP import get_ipv4

# Lista de nodos conectados (IP y puerto)
connected_nodes = []
coordinator_ip = None

def initialize_connections(local_ipv4):
    try:
        with open("remote_servers.txt", "r") as file:
            remote_servers = [line.strip().split() for line in file.readlines() if line.strip().split()[0] != local_ipv4]

        # Conectarse a cada servidor remoto en un hilo separado
        threads = []
        for ip, port in remote_servers:
            thread = threading.Thread(target=connect_to_remote_server, args=(ip, port))
            threads.append(thread)
            thread.start()

        # Esperar a que todos los hilos terminen
        for thread in threads:
            thread.join()

        # Iniciar la elección del coordinador después de establecer las conexiones
        start_election(local_ipv4)
    except Exception as e:
        print("Error al conectar con los servidores remotos:", e)

def connect_to_remote_server(ip, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((ip, int(port)))
            connected_nodes.append((ip, port))
            print("Conexión establecida con el servidor remoto en", ip, "en el puerto", port)
    except Exception as e:
        print(f"Error al conectar con el servidor remoto {ip}:{port}:", e)

def start_election(local_ipv4):
    global coordinator_ip

    print("Iniciando elección del coordinador...")
    highest_ip = local_ipv4
    for ip, port in connected_nodes:
        if ip > highest_ip:
            highest_ip = ip

    if highest_ip == local_ipv4:
        coordinator_ip = local_ipv4
        print("Soy el nuevo coordinador:", coordinator_ip)
        notify_nodes("COORDINATOR", coordinator_ip)
    else:
        coordinator_ip = highest_ip
        print("El nuevo coordinador es:", coordinator_ip)

    # Verificación periódica para asegurarse de que el coordinador está activo
    threading.Thread(target=monitor_coordinator).start()


def monitor_coordinator():
    global coordinator_ip

    while True:
        # Verificar si el coordinador está activo
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((coordinator_ip, 12345))  # Puerto donde el coordinador está escuchando
                s.sendall(b"HEARTBEAT")
                data = s.recv(1024)
                if data != b"HEARTBEAT":
                    raise Exception("Coordinador no responde.")
        except Exception as e:
            print(f"El coordinador {coordinator_ip} no está respondiendo. Iniciando nueva elección...")
            start_election(get_ipv4())  # Iniciar nueva elección de coordinador
            break  # Terminar monitoreo para reiniciar elección
        time.sleep(10)  # Esperar 10 segundos antes de volver a verificar



def notify_nodes(message, coordinator_ip):
    for ip, port in connected_nodes:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.connect((ip, int(port)))
                client_socket.sendall(f"{message} {coordinator_ip}".encode())
        except Exception as e:
            print(f"Error al notificar al nodo {ip}:{port}:", e)

def handle_incoming_messages():
    while True:
        # Este código debe manejar la recepción de mensajes de otros nodos
        # para actualizar el coordinador cuando se reciba un mensaje COORDINATOR.
        pass

if __name__ == "__main__":
    local_ipv4 = get_ipv4()
    initialize_connections(local_ipv4)
    threading.Thread(target=handle_incoming_messages).start()

