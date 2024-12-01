# **Chat-Sockets-Node**  
Chat TCP Seguro con Node.js  

## **Descripción**  
Esta es una aplicación de chat basada en el protocolo TCP desarrollada en Node.js. Permite la comunicación en tiempo real entre múltiples usuarios conectados a un servidor central. Además, incorpora mecanismos de cifrado y verificación de integridad para garantizar la seguridad de los mensajes transmitidos.  

---

## **Características**  

- **Cifrado de Mensajes**: Implementa AES-256-CBC para proteger la confidencialidad de los mensajes.  
- **Autenticación HMAC**: Verifica la integridad de los mensajes utilizando HMAC con SHA-256.  
- **Reconexión Automática**: El cliente intenta reconectarse al servidor en caso de desconexión.  
- **Diferenciación Visual de Mensajes**: Usa `chalk` para resaltar mensajes del servidor, notificaciones y mensajes de otros usuarios.  
- **Múltiples Clientes**: Soporta la conexión de múltiples usuarios simultáneamente.  

---

## **Requisitos del Sistema**  

- **Node.js** versión 14.0 o superior.  

---

## **Instalación**  

1. **Clona el repositorio:**  

   ```bash
   git clone https://github.com/tu-usuario/chat-sockets-node.git
   cd Sockets_node

2. **Instala las dependencias:**

   ```bash
   npm install
   
---

## **Uso**

 1. **Inicia el servidor**
   
     ```bash
     cd server
     node ./server.js

 2. **Inicia un cliente**
    
    En otra terminal ejecuta lo siguiente:
   
       ```bash
       cd client
       node ./client.js
       
---

## **Estructura de Archivos**
   ```bash
     📂 sockets_node
    ├── 📂 client 
    │    └── client.js
    ├── 📂 server 
    │    └── server.js
    ├── package.json
    ├── README.md
    └── node_modules/


