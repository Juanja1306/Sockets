const net = require('net');
const crypto = require('crypto');
const chalk = require('chalk'); // Importamos chalk
const ora = require('ora'); // Importamos ora

// Configuración para cifrado y HMAC
const ALGORITHM = 'aes-256-cbc';
const ENCRYPTION_KEY = '11111111111111111111111111111111'; // 32 bits
const IV = Buffer.from('0000000000000000'); // 16 bits
const HMAC_SECRET = 'admin123';

// Configuración de reconexión
const SERVER_HOST = '127.0.0.1';
const SERVER_PORT = 3000;
const RECONNECT_INTERVAL = 5000; // Tiempo en milisegundos (5 segundos)

let client = null;
let sessionData = { name: null }; // Almacenará los datos de sesión del cliente (como nombre de usuario)

// Usamos ora para mostrar un spinner de carga cuando nos conectamos al servidor
const spinner = ora('Conectando al servidor...').start();

// Función para cifrar mensajes
function encryptMessage(message) {
    const cipher = crypto.createCipheriv(ALGORITHM, ENCRYPTION_KEY, IV);
    let encrypted = cipher.update(message, 'utf8', 'hex');
    encrypted += cipher.final('hex');
    return encrypted;
}

// Función para generar HMAC
function generateHMAC(message) {
    return crypto.createHmac('sha256', HMAC_SECRET).update(message).digest('hex');
}

// Función para establecer la conexión con el servidor
function connectToServer() {
    client = net.createConnection({ host: SERVER_HOST, port: SERVER_PORT }, () => {
        spinner.succeed(chalk.green('Conectado al servidor.'));

        // Verificar si el cliente ya tiene datos de sesión guardados
        if (sessionData.name) {
            // Si tiene un nombre de usuario, lo envía automáticamente
            sendMessage(sessionData.name);
            requestMessage(); // Solicitar el primer mensaje del cliente
        } else {
            // Solicitar el nombre del usuario si no está guardado
            requestUsername();
        }
    });

    // Manejar mensajes recibidos del servidor
    client.on('data', (data) => {
        const message = data.toString().trim();

        if (message.includes('se ha conectado') || message.includes('se ha desconectado')) {
            // Mensajes de notificaciones de conexión/desconexión
            console.log(chalk.yellow.bold(message) + '\n');  // Añadir salto de línea
        } else if (message.includes('[SERVIDOR]')) {
            // Mensajes generales del servidor
            console.log(chalk.bgBlue.white.bold(` ${message} `) + '\n');  // Añadir salto de línea
        } else {
            // Mensajes de otros usuarios
            console.log(chalk.cyan(`[Mensaje recibido]: ${message}\n`));  // Mensajes con salto de línea
        }
    });

    // Manejar errores
    client.on('error', (err) => {
        spinner.fail(chalk.red('Error de conexión:', err.message));
    });

    // Manejar cierre de conexión
    client.on('close', () => {
        console.log(chalk.yellow('\nConexión cerrada.'));
        // Intentar reconectar cada 5 segundos
        setTimeout(connectToServer, RECONNECT_INTERVAL);
    });
}

// Función para solicitar el nombre de usuario
function requestUsername() {
    process.stdout.write(chalk.green('\nPor favor, ingresa tu nombre de usuario: '));

    // Eliminar cualquier oyente anterior para evitar acumulación de oyentes
    process.stdin.removeAllListeners('data');

    process.stdin.once('data', (input) => {
        const username = input.toString().trim();
        sessionData.name = username; // Guardar el nombre una sola vez
        sendMessage(username); // Enviar el nombre al servidor
        requestMessage(); // Luego de ingresar el nombre, solicitamos los mensajes
    });
}

// Función para enviar mensajes al servidor
function sendMessage(message) {
    const hmac = generateHMAC(message);
    const dataToSend = `${message}|${hmac}`;
    const encryptedMessage = encryptMessage(dataToSend);
    client.write(`${encryptedMessage}|`);
    console.log(chalk.greenBright(`[Enviado]: ${message}`));  // Mostrar mensaje enviado
}

// Función para solicitar un mensaje del usuario
function requestMessage() {
    // Eliminar cualquier prompt de "Escribe un mensaje:" para que no se muestre
    process.stdin.removeAllListeners('data'); // Limpiar el flujo de entrada anterior
    process.stdin.once('data', (input) => {
        const message = input.toString().trim();
        sendMessage(message); // Enviar el mensaje al servidor
        requestMessage(); // Pedir el siguiente mensaje sin mostrar prompt
    });
}

// Iniciar la conexión con el servidor
connectToServer();
