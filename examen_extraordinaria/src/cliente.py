import socket
import sys


HOST_POR_DEFECTO = "127.0.0.1"
PUERTO_POR_DEFECTO = 16063
TAMANO_BUFFER = 65535
TIMEOUT_POR_DEFECTO = 5.0
MINIMO_MENSAJES_CLIENTE = 3

COMANDO_NUMERO = "NUMERO"
COMANDO_SALIR = "SALIR"
RESPUESTA_OK = "OK"
MENSAJE_ERROR_COMUNICACION = "ERROR: no se pudo comunicar con el servidor"


class ClienteUDP:
    """Cliente UDP para enviar mensajes al servidor del ejercicio."""

    def __init__(
        self,
        host=HOST_POR_DEFECTO,
        puerto=PUERTO_POR_DEFECTO,
        timeout=TIMEOUT_POR_DEFECTO,
    ):
        self.host = host
        self.puerto = puerto
        self.timeout = timeout
        self.esta_cerrado = False
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(self.timeout)
        self.socket.connect((self.host, self.puerto))

    def enviar_mensaje(self, mensaje):
        self.socket.send(mensaje.encode("utf-8"))
        datos = self.socket.recv(TAMANO_BUFFER)
        return datos.decode("utf-8")

    def ejecutar_mensajes(self, mensajes, salida=None):
        salida = salida or sys.stdout

        for mensaje in mensajes:
            debe_terminar = self._enviar_e_imprimir(mensaje, salida)
            if debe_terminar is None:
                break
            if debe_terminar:
                return True

        return False

    def ejecutar_interactivo(self, entrada=None, salida=None):
        entrada = entrada or sys.stdin
        salida = salida or sys.stdout

        numero_mensaje = 1
        mensajes_enviados = 0

        while True:
            mensaje = self._leer_mensaje(entrada, mensajes_enviados)
            if not mensaje:
                break

            print(f"Mensaje {numero_mensaje}: {mensaje}", file=salida)
            debe_terminar = self.ejecutar_mensajes([mensaje], salida=salida)
            numero_mensaje += 1
            mensajes_enviados += 1

            if debe_terminar:
                break

    def cerrar(self):
        if not self.esta_cerrado:
            self.socket.close()
            self.esta_cerrado = True

    def _enviar_e_imprimir(self, mensaje, salida):
        try:
            respuesta = self.enviar_mensaje(mensaje)
        except OSError:
            print(MENSAJE_ERROR_COMUNICACION, file=salida)
            return None

        print(respuesta, file=salida)
        return self._es_salida_confirmada(mensaje, respuesta)

    def _es_salida_confirmada(self, mensaje, respuesta):
        return mensaje == COMANDO_SALIR and respuesta == RESPUESTA_OK

    def _leer_mensaje(self, entrada, mensajes_enviados):
        linea = entrada.readline()

        if linea:
            return linea.rstrip("\n")

        if mensajes_enviados >= MINIMO_MENSAJES_CLIENTE:
            return None

        if mensajes_enviados == MINIMO_MENSAJES_CLIENTE - 1:
            return COMANDO_SALIR

        return COMANDO_NUMERO
