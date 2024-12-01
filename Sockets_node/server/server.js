const net = require('net');
const crypto = require('crypto');
const chalk = require('chalk'); // Importamos chalk
const ora = require('ora'); // Importamos ora

// Configuración para cifrado y HMAC
const ALGORITHM = 'aes-256-cbc';
const ENCRYPTION_KEY = '11111111111111111111111111111111'; // 32 bytes
const IV = Buffer.from('0000000000000000'); // 16 bytes
const HMAC_SECRET = 'admin123';

// Persistencia de clientes
const clients = new Map(); // Almacena clientes por ID único

// Función para cifrar mensajes
function encryptMessage(message) {
    const cipher = crypto.createCipheriv(ALGORITHM, ENCRYPTION_KEY, IV);
    let encrypted = cipher.update(message, 'utf8', 'hex');
    encrypted += cipher.final('hex');
    return encrypted;
}

// Función para descifrar mensajes
function decryptMessage(encryptedMessage) {
    const decipher = crypto.createDecipheriv(ALGORITHM, ENCRYPTION_KEY, IV);
    let decrypted = decipher.update(encryptedMessage, 'hex', 'utf8');
    decrypted += decipher.final('utf8');
    return decrypted;
}

// Función para generar HMAC
function generateHMAC(message) {
    return crypto.createHmac('sha256', HMAC_SECRET).update(message).digest('hex');
}

// Función para verificar HMAC
function verifyHMAC(message, hmac) {
    const calculatedHMAC = generateHMAC(message);
    return hmac === calculatedHMAC;
}

// Manejo de conexiones de clientes
const server = net.createServer((socket) => {
    let clientId = null;  // ID único del cliente
    let clientName = null; // Nombre del cliente

    console.log(chalk.green.bold(`Cliente conectado: ${socket.remoteAddress}:${socket.remotePort}`));

    socket.on('data', (data) => {
        try {
            const [encryptedMessage] = data.toString().split('|');
            const decryptedData = decryptMessage(encryptedMessage).split('|');
            const [message, hmac] = decryptedData;

            // Verificar HMAC
            if (!verifyHMAC(message, hmac)) {
                console.log(chalk.red.bold('Error: Integridad del mensaje comprometida.'));
                socket.write('Error: Integridad del mensaje comprometida.\n');
                return;
            }

            // Asignar ID único a un nuevo cliente
            if (!clientId) {
                clientId = `${socket.remoteAddress}:${socket.remotePort}`;
            }

            // Registrar o actualizar cliente
            if (!clients.has(clientId)) {
                clientName = message; // El primer mensaje es el nombre
                if ([...clients.values()].some(client => client.name === clientName)) {
                    socket.write(chalk.yellow('Error: Nombre de usuario ya en uso.\n'));
                    socket.end(); // Cierra la conexión
                    return;
                }

                clients.set(clientId, { socket, name: clientName });
                console.log(chalk.blue.bold(`Nuevo cliente registrado: ${clientName} (ID: ${clientId})`));

                // Notificar a los demás clientes
                broadcast(`${clientName} se ha conectado.`, clientId);
            } else {
                // Procesar mensajes normales
                if (message) {
                    broadcast(`${clientName}: ${message}`, clientId);
                }
            }
        } catch (err) {
            console.error(chalk.red.bold('Error al procesar el mensaje:', err.message));
        }
    });

    socket.on('close', () => {
        if (clientId && clients.has(clientId)) {
            console.log(chalk.yellow.bold(`\nCliente desconectado: ${clientId}`));
            clients.delete(clientId);
            broadcast(`${clientName} se ha desconectado.`, clientId);
        }
    });

    socket.on('error', (err) => {
        console.error(chalk.red.bold('Error en el cliente:', err.message));
    });
});

// Función para difundir mensajes a todos los clientes excepto el remitente
function broadcast(message, senderId) {
    clients.forEach((client, id) => {
        if (id !== senderId) {
            client.socket.write(`${chalk.green.bold(message)}\n`);  // Añadir salto de línea
        }
    });
}

// Usamos ora para mostrar un spinner mientras el servidor está escuchando
const spinner = ora('Servidor TCP escuchando en el puerto 3000').start();
server.listen(3000, () => {
    spinner.succeed(chalk.cyan.bold('Servidor en línea y escuchando en el puerto 3000'));
});
