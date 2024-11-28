import socket
import threading
import ssl
import hmac
import hashlib
import tkinter as tk
from tkinter import simpledialog
import time

# Clave secreta compartida entre cliente y servidor para HMAC
secret_key = b'supersecretkey123'

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

# Función para generar un HMAC (hash con clave) de un mensaje
def generate_hmac(message):
    return hmac.new(secret_key, message.encode('utf-8'), hashlib.sha256).hexdigest()

# Función para verificar la integridad de un mensaje usando HMAC
def verify_hmac(message, received_hmac):
    calculated_hmac = generate_hmac(message)
    return hmac.compare_digest(calculated_hmac, received_hmac)

# Función para recibir mensajes y actualizar la interfaz
def receive_messages(secure_client_socket, text_area, root, client_listbox):
    while True:
        try:
            data = secure_client_socket.recv(2048).decode('utf-8')
            if not data:
                break

            try:
                message, received_hmac = data.rsplit('|', 1)
            except ValueError:
                print("Mensaje recibido en un formato inválido.")
                continue

            if verify_hmac(message, received_hmac):
                # Mostrar el mensaje en el área de texto
                root.after(0, update_text_area, message, text_area)
                # Si el mensaje contiene la lista de usuarios
                if message.startswith("Lista de usuarios:"):
                    # Actualizar la lista de clientes conectados
                    root.after(0, update_client_list, message, client_listbox)
            else:
                print("Advertencia: Mensaje recibido con HMAC inválido.")
        except Exception as e:
            print(f"Error al recibir mensaje: {e}")
            break

# Función para actualizar el área de texto con un nuevo mensaje
def update_text_area(message, text_area):
    text_area.config(state=tk.NORMAL)
    text_area.insert(tk.END, message + "\n")
    text_area.config(state=tk.DISABLED)
    text_area.yview(tk.END)

# Función para actualizar la lista de clientes conectados
def update_client_list(message, client_listbox):
    # Extraemos los nombres de los usuarios de la cadena del mensaje
    user_list = message.split(":")[1].strip()
    user_list = eval(user_list)  # Convertir el string en una lista de usuarios

    # Limpiar la lista de usuarios actual
    client_listbox.delete(0, tk.END)

    # Insertar los usuarios en el Listbox
    for user in user_list:
        client_listbox.insert(tk.END, user)

# Función para manejar el evento de enviar un mensaje
def send_message(event, secure_client_socket, entry_field, nickname, text_area):
    message = entry_field.get()
    if message.lower() == "salir":
        secure_client_socket.close()
        root.quit()
    else:
        try:
            # Mostrar el mensaje localmente con el prefijo "Tu:" antes de enviarlo
            update_text_area(f"Tu: {message}", text_area)
            
            hmac_hash = generate_hmac(message)
            secure_client_socket.send(f"{message}|{hmac_hash}".encode('utf-8'))
            entry_field.delete(0, tk.END)  # Limpiar el campo de entrada
        except Exception as e:
            print(f"Error al enviar el mensaje: {e}")
            print("Intentando reconectar...")
            secure_client_socket.close()
            secure_client_socket = reconnect_to_server()

# Función para iniciar el cliente
def start_client():
    secure_client_socket = reconnect_to_server()

    # Iniciar una nueva ventana de Tkinter
    global root
    root = tk.Tk()

    # Pedir el nickname al usuario
    nickname = simpledialog.askstring("Nickname", "Ingresa tu nickname:")
    if not nickname:
        nickname = "Invitado"  # Default nickname

    # Cambiar el título de la ventana a "Chat - [nickname]"
    root.title(f"Chat - {nickname}")

    # Crear una área de texto para mostrar los mensajes
    text_area = tk.Text(root, height=15, width=50, state=tk.DISABLED)
    text_area.pack(padx=10, pady=10)

    # Crear un campo de entrada para escribir el mensaje
    entry_field = tk.Entry(root, width=40)
    entry_field.pack(padx=10, pady=10)
    entry_field.bind("<Return>", lambda event: send_message(event, secure_client_socket, entry_field, nickname, text_area))

    # Crear un Listbox para mostrar los clientes conectados
    client_listbox_label = tk.Label(root, text="Clientes Conectados:")
    client_listbox_label.pack(pady=5)
    
    client_listbox = tk.Listbox(root, height=10, width=20)
    client_listbox.pack(padx=10, pady=10)

    secure_client_socket.send(nickname.encode('utf-8'))

    # Iniciar un hilo para recibir mensajes
    threading.Thread(target=receive_messages, args=(secure_client_socket, text_area, root, client_listbox), daemon=True).start()

    # Iniciar la interfaz gráfica de Tkinter
    root.mainloop()

if __name__ == "__main__":
    start_client()
