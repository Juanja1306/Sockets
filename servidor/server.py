import socket
import threading
import ssl
import hmac
import hashlib
import os
import json
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption, PrivateFormat
import datetime

# Diccionario para manejar los clientes y sus apodos (nicknames)
clients = {}  # Ahora sólo almacena los nicknames de los clientes
secret_key = b'supersecretkey123'  # Clave secreta para los HMAC
nicknames_file = 'nicknames.json'  # Archivo donde se guardan los nicknames de los clientes

# Función para generar un HMAC (hash con clave) de un mensaje
def generate_hmac(message):
    return hmac.new(secret_key, message.encode('utf-8'), hashlib.sha256).hexdigest()

# Función para verificar la integridad de un mensaje usando HMAC
def verify_hmac(message, received_hmac):
    calculated_hmac = generate_hmac(message)
    return hmac.compare_digest(calculated_hmac, received_hmac)

# Cargar nicknames desde un archivo JSON
def load_nicknames():
    if os.path.exists(nicknames_file):
        with open(nicknames_file, 'r') as file:
            nicknames = json.load(file)
            # Crear un diccionario con los nicknames como claves
            return {nickname: None for nickname in nicknames}
    return {}

# Guardar los nicknames en un archivo JSON
def save_nicknames():
    with open(nicknames_file, 'w') as file:
        json.dump(list(clients.keys()), file)  # Solo guardamos los nicknames

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
                #save_nicknames()  # Guardar estado después de desconexión

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
            #save_nicknames()

# Función para manejar las conexiones de los clientes
def handle_client(client_socket, client_address):
    try:
        nickname = client_socket.recv(1024).decode('utf-8')

        if nickname not in clients:
            clients[nickname] = client_socket
            print(f"{nickname} se ha conectado.")
            #save_nicknames()

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
        #save_nicknames()

# Generar claves y certificados temporales
def generate_temp_cert():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    subject = issuer = x509.Name([ 
        x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "California"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "San Francisco"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Chat Application"),
        x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
    ])

    certificate = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.datetime.now(datetime.timezone.utc)
    ).not_valid_after(
        datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1)
    ).sign(private_key, hashes.SHA256())

    # Exportar clave privada y certificado
    key_pem = private_key.private_bytes(
        encoding=Encoding.PEM,
        format=PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=NoEncryption(),
    )
    cert_pem = certificate.public_bytes(Encoding.PEM)

    # Guardar temporalmente en archivos
    with open("temp_server.key", "wb") as key_file:
        key_file.write(key_pem)
    with open("temp_server.crt", "wb") as cert_file:
        cert_file.write(cert_pem)

# Iniciar servidor
def start_server():
    host = '127.0.0.1'
    port = 5555

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)

    # Cargar los nicknames de los clientes desde el archivo
    global clients
    #clients = load_nicknames()

    # Generar certificado y clave temporal
    generate_temp_cert()

    # Crear contexto SSL
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile="temp_server.crt", keyfile="temp_server.key")

    print(f"Servidor seguro iniciado en {host}:{port}")

    while True:
        try:
            client_socket, addr = server.accept()
            secure_client_socket = context.wrap_socket(client_socket, server_side=True)
            print(f"Conexión segura desde {addr}")
            threading.Thread(target=handle_client, args=(secure_client_socket, addr), daemon=True).start()
        except Exception as e:
            print(f"Error al aceptar una nueva conexión: {e}")

if __name__ == "__main__":
    start_server()
