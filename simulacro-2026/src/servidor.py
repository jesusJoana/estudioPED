import socket
from datetime import datetime


MENSAJE_FECHA = "FECHA"
MENSAJE_HORA = "HORA"
RESPUESTA_ERROR = "ERROR"
FORMATO_FECHA = "%Y-%m-%d"
FORMATO_HORA = "%H:%M:%S"
TAM_BUFFER = 1024


class ServidorTCP:
    """Servidor TCP sencillo para responder a los mensajes del protocolo."""

    def __init__(self, host="127.0.0.1", puerto=16063):
        self.host = host
        self.puerto = puerto

    def procesar_mensaje(self, mensaje):
        """Devuelve la respuesta correspondiente al mensaje recibido."""
        mensaje = mensaje.strip()

        if mensaje == MENSAJE_FECHA:
            return datetime.now().strftime(FORMATO_FECHA)
        if mensaje == MENSAJE_HORA:
            return datetime.now().strftime(FORMATO_HORA)

        return RESPUESTA_ERROR

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

            while self._debe_aceptar_conexiones(conexiones_atendidas, max_conexiones):
                conexion, _ = servidor.accept()
                with conexion:
                    self.atender_conexion(conexion)
                conexiones_atendidas += 1

    def atender_conexion(self, conexion):
        """Lee un mensaje de una conexion y envia la respuesta."""
        datos = conexion.recv(TAM_BUFFER)
        mensaje = datos.decode("utf-8").strip()
        respuesta = self.procesar_mensaje(mensaje)
        conexion.sendall((respuesta + "\n").encode("utf-8"))

    def _debe_aceptar_conexiones(self, conexiones_atendidas, max_conexiones):
        """Indica si el servidor debe seguir aceptando conexiones."""
        return max_conexiones is None or conexiones_atendidas < max_conexiones
