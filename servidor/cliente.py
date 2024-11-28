import socket
import ssl
import threading
import hmac
import hashlib
import time

# Clave secreta compartida entre cliente y servidor para HMAC
secret_key = b'supersecretkey123'

# Función para generar un HMAC (hash con clave) de un mensaje
def generate_hmac(message):
    return hmac.new(secret_key, message.encode('utf-8'), hashlib.sha256).hexdigest()

# Función para verificar la integridad de un mensaje usando HMAC
def verify_hmac(message, received_hmac):
    calculated_hmac = generate_hmac(message)
    return hmac.compare_digest(calculated_hmac, received_hmac)

# Función para recibir mensajes del servidor
def receive_messages(secure_client_socket):
    while True:
        try:
            data = secure_client_socket.recv(2048).decode('utf-8')
            if not data:
                break
            
            # Separar mensaje y HMAC recibido
            try:
                message, received_hmac = data.rsplit('|', 1)
            except ValueError:
                print("Mensaje recibido en un formato inválido.")
                continue
            
            # Verificar integridad del mensaje
            if verify_hmac(message, received_hmac):
                print(message)
            else:
                print("Advertencia: Mensaje recibido con HMAC inválido. Podría estar corrupto.")
        except Exception as e:
            print(f"Error al recibir mensaje: {e}")
            break

# Función para intentar reconectar al servidor
def reconnect_to_server():
    while True:
        try:
            print("Intentando conectar al servidor...")
            host = '127.0.0.1'
            port = 5555

            # Crear contexto SSL
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE  # Permitir certificados temporales (autofirmados)

            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            secure_client_socket = context.wrap_socket(client_socket, server_hostname=host)
            secure_client_socket.connect((host, port))

            print("Conexión segura establecida con el servidor.")
            return secure_client_socket
        except Exception as e:
            print(f"Error de conexión: {e}")
            print("Reintentando en 5 segundos...")
            time.sleep(5)

# Función principal para iniciar el cliente
def start_client():
    secure_client_socket = reconnect_to_server()

    # Enviar el nickname al servidor
    nickname = input("Ingresa tu nickname: ")
    secure_client_socket.send(nickname.encode('utf-8'))

    # Iniciar un hilo para recibir mensajes
    threading.Thread(target=receive_messages, args=(secure_client_socket,), daemon=True).start()

    while True:
        try:
            message = input()
            if message.lower() == "salir":
                secure_client_socket.close()
                break

            # Generar HMAC para el mensaje
            hmac_hash = generate_hmac(message)

            # Enviar mensaje con HMAC
            secure_client_socket.send(f"{message}|{hmac_hash}".encode('utf-8'))
        except Exception as e:
            print(f"Error al enviar el mensaje: {e}")
            print("Intentando reconectar...")
            secure_client_socket.close()
            secure_client_socket = reconnect_to_server()

if __name__ == "__main__":
    start_client()
