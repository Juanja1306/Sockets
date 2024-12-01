# Descripción del Proyecto

Este proyecto implementa un sistema de chat seguro basado en sockets TCP y asegura la comunicación entre clientes y servidor mediante HMAC (Hash-Based Message Authentication Code). 

## Componentes principales:

1. **Servidor de chat**: Coordina las comunicaciones entre los clientes y verifica la autenticidad de los mensajes.
2. **Cliente de chat**: Proporciona una interfaz gráfica para enviar y recibir mensajes.

El sistema garantiza la integridad y autenticidad de los mensajes mediante el uso de una clave secreta compartida.

---

## Requisitos Previos

Antes de ejecutar el sistema, asegúrate de cumplir con los siguientes requisitos:

- **Python 3.9 o superior** instalado en tu sistema.
- Librerías estándar de Python (no se necesitan instalaciones adicionales).
- Una red local configurada para permitir conexiones en el puerto `5555`.

---

## Cómo Ejecutar el Sistema

### 1. Servidor

1. **Ubicación del archivo**: Asegúrate de tener el archivo `server.py` en tu sistema.
2. **Pasos**:
   - Abre una terminal.
   - Navega al directorio donde se encuentra `server.py`.
   - Ejecuta el comando:

     ```bash
     python server.py
     ```

3. **Estado**:
   - Verás mensajes en la terminal indicando:
     - Conexiones entrantes.
     - Desconexiones.
     - Errores y mensajes transmitidos.

4. **Por defecto**:
   - El servidor se ejecutará en `127.0.0.1` (localhost) en el puerto `5555`.

---

### 2. Cliente

1. **Ubicación del archivo**: Asegúrate de tener el archivo `cliente.py` en tu sistema.
2. **Pasos**:
   - Abre una terminal.
   - Navega al directorio donde se encuentra `cliente.py`.
   - Ejecuta el comando:

     ```bash
     python cliente.py
     ```

3. **Interacción**:
   - Se abrirá una interfaz gráfica donde podrás:
     - Ingresar tu nickname (se pedirá al inicio).
     - Enviar mensajes al chat público.
     - Ver una lista de usuarios conectados.

4. **Reconexión Automática**:
   - Si la conexión con el servidor se pierde, el cliente intentará reconectarse automáticamente cada 5 segundos.

---

## Seguridad

- **HMAC**: Cada mensaje incluye un HMAC calculado con una clave secreta compartida entre servidor y clientes. Esto asegura la integridad de los mensajes en tránsito.
- **Clave secreta**: Está definida en los archivos `server.py` y `cliente.py`. **Debe mantenerse privada y no compartirse con terceros.**
- **Rechazo de mensajes corruptos**: Los mensajes con un HMAC inválido son descartados automáticamente.

---

## Notas Adicionales

1. **Configuración de IP**: Este sistema está configurado para ejecutarse en `localhost` por defecto. Para ejecutarlo en una red, actualiza la dirección IP en ambos archivos.
2. **Puerto**: Si el puerto `5555` ya está en uso, puedes cambiarlo en los archivos.
3. **Detener el servidor**: Usa `CTRL+C` en la terminal donde se ejecuta el servidor para detenerlo manualmente.

---

¡Disfruta del sistema de chat seguro! Si tienes dudas o problemas, revisa los comentarios en los archivos del código.
