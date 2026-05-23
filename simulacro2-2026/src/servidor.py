import socket
from datetime import datetime


class ServidorUDP:
    """Servidor UDP que atiende mensajes FECHA y HORA."""

    MENSAJE_FECHA = "FECHA"
    MENSAJE_HORA = "HORA"
    RESPUESTA_ERROR = "ERROR"
    FORMATO_FECHA = "%d/%m/%Y"
    FORMATO_HORA = "%H:%M:%S"
    TAMANO_BUFFER = 1024
    TIMEOUT_SOCKET = 0.2

    def __init__(self, host="0.0.0.0", puerto=16063):
        self.host = host
        self.puerto = puerto
        self._activo = False
        self._socket = None

    def procesar_mensaje(self, mensaje):
        if mensaje == self.MENSAJE_FECHA:
            return datetime.now().strftime(self.FORMATO_FECHA)
        if mensaje == self.MENSAJE_HORA:
            return datetime.now().strftime(self.FORMATO_HORA)
        return self.RESPUESTA_ERROR

    def iniciar(self, max_mensajes=None):
        self._activo = True
        mensajes_procesados = 0

        with self._crear_socket() as servidor:
            self._socket = servidor

            while self._activo:
                if max_mensajes is not None and mensajes_procesados >= max_mensajes:
                    break

                try:
                    datos, direccion = servidor.recvfrom(self.TAMANO_BUFFER)
                except socket.timeout:
                    continue

                self._responder_datagrama(datos, direccion, servidor)
                mensajes_procesados += 1

        self._socket = None
        self._activo = False

    def detener(self):
        self._activo = False

    def _crear_socket(self):
        servidor = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        servidor.bind((self.host, self.puerto))
        self.puerto = servidor.getsockname()[1]
        servidor.settimeout(self.TIMEOUT_SOCKET)
        return servidor

    def _responder_datagrama(self, datos, direccion, servidor):
        mensaje = datos.decode("utf-8")
        respuesta = self.procesar_mensaje(mensaje)
        servidor.sendto(respuesta.encode("utf-8"), direccion)
