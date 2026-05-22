import socket
import sys


HOST_POR_DEFECTO = "127.0.0.1"
PUERTO_POR_DEFECTO = 16063
TAMANO_BUFFER = 65535
TIMEOUT_POR_DEFECTO = 5.0
MINIMO_MENSAJES_CLIENTE = 3
PUERTO_MINIMO = 1
PUERTO_MAXIMO = 65535

COMANDO_NUMERO = "NUMERO"
COMANDO_SALIR = "SALIR"
RESPUESTA_OK = "OK"
MENSAJE_ERROR_COMUNICACION = "ERROR: no se pudo comunicar con el servidor"
MENSAJE_ERROR_DIRECCION = "ERROR: direccion del servidor no valida"
PROMPT_DIRECCION_SERVIDOR = "Direccion completa del servidor (host:puerto): "


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

    @classmethod
    def parsear_direccion_servidor(cls, direccion):
        partes = direccion.strip().split(":")
        if len(partes) != 2:
            raise ValueError(MENSAJE_ERROR_DIRECCION)

        host, puerto_texto = partes
        if not host or not puerto_texto:
            raise ValueError(MENSAJE_ERROR_DIRECCION)

        try:
            puerto = int(puerto_texto)
        except ValueError as exc:
            raise ValueError(MENSAJE_ERROR_DIRECCION) from exc

        if not cls._puerto_es_valido(puerto):
            raise ValueError(MENSAJE_ERROR_DIRECCION)

        return host, puerto

    @classmethod
    def pedir_direccion_servidor(cls, entrada=None, salida=None):
        entrada = entrada or sys.stdin
        salida = salida or sys.stdout

        print(PROMPT_DIRECCION_SERVIDOR, end="", file=salida, flush=True)
        direccion = entrada.readline().strip()
        return cls.parsear_direccion_servidor(direccion)

    @classmethod
    def ejecutar_desde_terminal(cls, entrada=None, salida=None, timeout=TIMEOUT_POR_DEFECTO):
        entrada = entrada or sys.stdin
        salida = salida or sys.stdout

        try:
            cliente = cls._crear_desde_entrada(entrada, salida, timeout)
        except ValueError:
            print(MENSAJE_ERROR_DIRECCION, file=salida)
            return
        except OSError:
            print(MENSAJE_ERROR_COMUNICACION, file=salida)
            return

        try:
            cliente.ejecutar_interactivo(entrada=entrada, salida=salida)
        finally:
            cliente.cerrar()

    @classmethod
    def _crear_desde_entrada(cls, entrada, salida, timeout):
        host, puerto = cls.pedir_direccion_servidor(entrada=entrada, salida=salida)
        return cls(host=host, puerto=puerto, timeout=timeout)

    @classmethod
    def _puerto_es_valido(cls, puerto):
        return PUERTO_MINIMO <= puerto <= PUERTO_MAXIMO

    def enviar_mensaje(self, mensaje):
        self.socket.send(mensaje.encode("utf-8"))
        datos = self.socket.recv(TAMANO_BUFFER)
        return datos.decode("utf-8")

    def ejecutar_mensajes(self, mensajes, salida=None):
        salida = salida or sys.stdout

        for mensaje in mensajes:
            resultado = self._enviar_e_imprimir(mensaje, salida)
            if resultado is None:
                break
            if resultado:
                return True

        return False

    def ejecutar_interactivo(self, entrada=None, salida=None):
        entrada = entrada or sys.stdin
        salida = salida or sys.stdout

        numero_mensaje = 1
        mensajes_enviados = 0

        while True:
            mensaje = self._obtener_siguiente_mensaje(entrada, mensajes_enviados)
            if not mensaje:
                break

            self._imprimir_mensaje(numero_mensaje, mensaje, salida)
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

    def _obtener_siguiente_mensaje(self, entrada, mensajes_enviados):
        linea = entrada.readline()

        if linea:
            return linea.rstrip("\n")

        return self._mensaje_automatico_para_completar_minimo(mensajes_enviados)

    def _mensaje_automatico_para_completar_minimo(self, mensajes_enviados):
        if mensajes_enviados >= MINIMO_MENSAJES_CLIENTE:
            return None

        if mensajes_enviados == MINIMO_MENSAJES_CLIENTE - 1:
            return COMANDO_SALIR

        return COMANDO_NUMERO

    def _imprimir_mensaje(self, numero_mensaje, mensaje, salida):
        print(f"Mensaje {numero_mensaje}: {mensaje}", file=salida)
