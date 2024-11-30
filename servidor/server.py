import socket
import threading
import hmac
import hashlib
import os

# Diccionario para manejar los clientes y sus apodos (nicknames)
clients = {}  # Ahora sólo almacena los nicknames de los clientes
secret_key = b'a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2g3h4i5j6k7l8m9n0o1p2q3r4s5t6u7v8w9x0y1z2a3b4c5d6e7f8g9h0i1j2k3l4m5n6o7p8q9r0s1t2u3v4w5x6y7z8a9b0c1d2e3f4g5h6i7j8k9l0m1n2o3p4'  # Clave secreta para los HMAC

# Función para generar un HMAC (hash con clave) de un mensaje
def generate_hmac(message):
    return hmac.new(secret_key, message.encode('utf-8'), hashlib.sha256).hexdigest()

# Función para verificar la integridad de un mensaje usando HMAC
def verify_hmac(message, received_hmac):
    calculated_hmac = generate_hmac(message)
    return hmac.compare_digest(calculated_hmac, received_hmac)

# Cargar nicknames desde un archivo JSON
# Función para retransmitir mensajes a todos los clientes conectados
def broadcast(message, sender_socket=None):
    for nickname, client_socket in clients.items():
        if client_socket != sender_socket:  # No enviar el mensaje al remitente
            try:
                hmac_hash = generate_hmac(message)
                client_socket.send(f"{message}|{hmac_hash}".encode('utf-8'))
            except Exception as e:
                print(f"Error al enviar mensaje a {nickname}: {e}")
                client_socket.close()
                del clients[nickname]

# Función para retransmitir la lista de clientes conectados a todos los clientes
def broadcast_user_list():
    user_list = list(clients.keys())  # Obtener los nombres de los clientes conectados
    user_list_message = f"Lista de usuarios: {user_list}"
    
    # Enviar la lista de usuarios a todos los clientes conectados
    for client_socket in clients.values():
        try:
            hmac_hash = generate_hmac(user_list_message)
            client_socket.send(f"{user_list_message}|{hmac_hash}".encode('utf-8'))
        except Exception as e:
            print(f"Error al enviar la lista de usuarios: {e}")
            client_socket.close()
            del clients[client_socket]

# Función para manejar las conexiones de los clientes
def handle_client(client_socket, client_address):
    try:
        nickname = client_socket.recv(1024).decode('utf-8')

        if nickname not in clients:
            clients[nickname] = client_socket
            print(f"{nickname} se ha conectado.")

        # Notificar a todos los clientes conectados sobre la nueva conexión
        broadcast(f"{nickname} se ha unido al chat.", sender_socket=None)

        # Enviar la lista de usuarios a todos los clientes
        broadcast_user_list()

        while True:
            data = client_socket.recv(2048).decode('utf-8')
            if not data:
                break
            
            try:
                message, received_hmac = data.rsplit('|', 1)
            except ValueError:
                print("Formato de mensaje inválido.")
                continue

            if verify_hmac(message, received_hmac):
                broadcast(f"{nickname}: {message}", sender_socket=client_socket)
            else:
                print(f"Mensaje corrupto recibido de {nickname}, descartando.")
                
    except Exception as e:
        print(f"Error en la conexión con el cliente: {e}")
    finally:
        if nickname in clients:
            del clients[nickname]
            print(f"{nickname} se ha desconectado.")
            broadcast(f"{nickname} ha salido del chat.")
            
            # Enviar la lista de usuarios actualizada
            broadcast_user_list()
        
        client_socket.close()

# Iniciar servidor
def start_server():
    host = '127.0.0.1'
    port = 5555

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)

    # Cargar los nicknames de los clientes desde el archivo
    global clients

    print(f"Servidor seguro iniciado en {host}:{port}")

    while True:
        try:
            client_socket, addr = server.accept()
            print(f"Conexión segura desde {addr}")
            threading.Thread(target=handle_client, args=(client_socket, addr), daemon=True).start()
        except Exception as e:
            print(f"Error al aceptar una nueva conexión: {e}")
        """except KeyboardInterrupt:
            print("Servidor detenido.")
            break"""

if __name__ == "__main__":
    start_server()
