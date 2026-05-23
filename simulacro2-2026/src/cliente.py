import socket


class ClienteUDP:
    """Cliente UDP interactivo para comunicarse con el servidor."""

    ORDEN_SALIR = "SALIR"
    MIN_MENSAJES_PARA_SALIR = 3
    TAMANO_BUFFER = 1024
    MENSAJE_ERROR_COMUNICACION = "Error de comunicacion con el servidor"
    MENSAJE_SALIDA_DENEGADA = (
        "Aun no es posible salir. Debes enviar al menos 3 mensajes al servidor."
    )
    MENSAJE_FIN_CLIENTE = "Cliente finalizado correctamente."

    def __init__(self, host_servidor="127.0.0.1", puerto=16063, timeout=2):
        self.host_servidor = host_servidor
        self.puerto = puerto
        self.timeout = timeout
        self.mensajes_enviados = 0

    def enviar_mensaje(self, mensaje):
        try:
            with self._crear_socket() as cliente:
                cliente.settimeout(self.timeout)
                cliente.sendto(
                    mensaje.encode("utf-8"),
                    (self.host_servidor, self.puerto),
                )
                datos, _ = cliente.recvfrom(self.TAMANO_BUFFER)
                return datos.decode("utf-8")
        except OSError as error:
            print(f"{self.MENSAJE_ERROR_COMUNICACION}: {error}")
            return None

    def procesar_entrada(self, mensaje):
        if mensaje == self.ORDEN_SALIR:
            return self._procesar_salida()

        respuesta = self.enviar_mensaje(mensaje)
        self.mensajes_enviados += 1

        if respuesta is not None:
            print(respuesta)

        return True

    def ejecutar(self):
        self.host_servidor = input("Introduce la direccion del servidor: ")
        self.ejecutar_interactivo()

    def ejecutar_interactivo(self):
        continuar = True
        while continuar:
            mensaje = input("Mensaje: ")
            continuar = self.procesar_entrada(mensaje)

        print(self.MENSAJE_FIN_CLIENTE)

    def _procesar_salida(self):
        if not self._puede_salir():
            print(self.MENSAJE_SALIDA_DENEGADA)
            return True
        return False

    def _puede_salir(self):
        return self.mensajes_enviados >= self.MIN_MENSAJES_PARA_SALIR

    def _crear_socket(self):
        return socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
