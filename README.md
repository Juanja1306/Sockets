# Sockets
Sockets usando python de tipo Clientes - Servidor


# Proyecto: Chat Grupal en Tiempo Real

Este proyecto consiste en el desarrollo de una aplicación de comunicación grupal en tiempo real, implementando sockets TCP para gestionar la comunicación cliente-servidor. Además, se aplicarán técnicas de seguridad y se presentará un informe detallado y un video demostrativo del funcionamiento del sistema.

---

## Objetivos

1. **Investigación sobre Sockets**: Ampliar el conocimiento sobre los mecanismos de comunicación en red, específicamente en lo relacionado con el uso de sockets.
   
2. **Desarrollo de la Aplicación de Chat**:
   - **Arquitectura Centralizada**:
     Diseñar un sistema cliente-servidor donde múltiples clientes puedan conectarse al servidor central para intercambiar mensajes en tiempo real.
   - **Implementación de Sockets TCP**:
     Establecer la comunicación entre los nodos del sistema utilizando sockets TCP.
   - **Protocolo de Comunicación Seguro**:
     Implementar mecanismos de seguridad como:
       - Encriptación de los datos.
       - Verificación de la integridad de los mensajes.
   - **Gestión de Conexiones**:
     Manejar eficazmente las conexiones y desconexiones de los clientes:
       - Permitir reconexión automática tras desconexiones.
       - Gestión de recursos para usuarios desconectados.
   - **Interfaz de Usuario Amigable**:
     Diseñar una interfaz gráfica que permita:
       - Conectarse al servidor.
       - Enviar y recibir mensajes en tiempo real.

3. **Demostración en Video**:
   Realizar un video donde se muestre el funcionamiento de la aplicación en distintos escenarios.

4. **Informe Técnico**:
   Preparar un informe detallado que documente:
   - El proceso de diseño y desarrollo.
   - La implementación de las funcionalidades.
   - La justificación de las decisiones tomadas.

---

## Requisitos Técnicos

- **Lenguaje de Programación**: Python o cualquier lenguaje que soporte sockets TCP y GUI.
- **Protocolo de Comunicación**: TCP.
- **Librerías recomendadas**:
  - Seguridad: `ssl`, `cryptography`.
  - Sockets: `socket`, `selectors`.
  - Interfaz gráfica: `Tkinter`, `PyQt`, o equivalente.
- **Entorno de desarrollo**: Entorno compatible con sockets TCP.

---

## Estructura del Proyecto

### Directorios

