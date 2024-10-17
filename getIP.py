import socket

def get_ipv4():
    try:
        # Crear un socket IPv4
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            # Conectar el socket a un servidor de nombres de dominio (DNS)
            s.connect(("8.8.8.8", 80))
            # Obtener la dirección IP local asociada al socket
            ip_address = s.getsockname()[0]
            return ip_address
    except Exception as e:
        print("Error al obtener la dirección IP:", e)
        return None

# if __name__ == "__main__":
#     ipv4 = get_ipv4()
#     if ipv4:
#         print("Dirección IPv4 de la máquina:", ipv4)
#     else:
#         print("No se pudo obtener la dirección IPv4.")
