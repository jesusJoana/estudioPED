import socket
from datetime import datetime


class ServidorUDP:
    """Servidor UDP que atiende mensajes FECHA y HORA."""

    def __init__(self, host="0.0.0.0", puerto=16063):
        self.host = host
        self.puerto = puerto
        self._activo = False
        self._socket = None

    def procesar_mensaje(self, mensaje):
        if mensaje == "FECHA":
            return datetime.now().strftime("%d/%m/%Y")
        if mensaje == "HORA":
            return datetime.now().strftime("%H:%M:%S")
        return "ERROR"

    def iniciar(self, max_mensajes=None):
        self._activo = True
        mensajes_procesados = 0

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as servidor:
            self._socket = servidor
            servidor.bind((self.host, self.puerto))
            self.puerto = servidor.getsockname()[1]
            servidor.settimeout(0.2)

            while self._activo:
                if max_mensajes is not None and mensajes_procesados >= max_mensajes:
                    break

                try:
                    datos, direccion = servidor.recvfrom(1024)
                except socket.timeout:
                    continue

                mensaje = datos.decode("utf-8")
                respuesta = self.procesar_mensaje(mensaje)
                servidor.sendto(respuesta.encode("utf-8"), direccion)
                mensajes_procesados += 1

        self._socket = None
        self._activo = False

    def detener(self):
        self._activo = False
