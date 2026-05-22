import socket
from datetime import datetime


class ServidorTCP:
    """Servidor TCP sencillo para responder a los mensajes del protocolo."""

    def __init__(self, host="127.0.0.1", puerto=16063):
        self.host = host
        self.puerto = puerto

    def procesar_mensaje(self, mensaje):
        """Devuelve la respuesta correspondiente al mensaje recibido."""
        mensaje = mensaje.strip()

        if mensaje == "FECHA":
            return datetime.now().strftime("%Y-%m-%d")
        if mensaje == "HORA":
            return datetime.now().strftime("%H:%M:%S")

        return "ERROR"

    def iniciar(self, max_conexiones=None):
        """
        Arranca el servidor. Si max_conexiones es None, queda escuchando de
        forma continua; en tests se limita para evitar bloqueos.
        """
        conexiones_atendidas = 0

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
            servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            servidor.bind((self.host, self.puerto))
            servidor.listen()

            # Si se pidio puerto 0, el sistema asigna uno libre y lo guardamos.
            self.puerto = servidor.getsockname()[1]

            while max_conexiones is None or conexiones_atendidas < max_conexiones:
                conexion, _ = servidor.accept()
                with conexion:
                    self.atender_conexion(conexion)
                conexiones_atendidas += 1

    def atender_conexion(self, conexion):
        """Lee un mensaje de una conexion y envia la respuesta."""
        datos = conexion.recv(1024)
        mensaje = datos.decode("utf-8").strip()
        respuesta = self.procesar_mensaje(mensaje)
        conexion.sendall((respuesta + "\n").encode("utf-8"))
