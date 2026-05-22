import socket


HOST_POR_DEFECTO = "127.0.0.1"
PUERTO_POR_DEFECTO = 16063
RUTAS_POR_DEFECTO = ["/etc/services", "/etc/passwd"]
TAMANO_BUFFER = 65535
MINIMO_MENSAJES_SALIR = 3

COMANDO_BUSCAR = "BUSCAR"
COMANDO_NUMERO = "NUMERO"
COMANDO_SALIR = "SALIR"

RESPUESTA_ERROR = "ERROR"
RESPUESTA_OK = "OK"


class ServidorUDP:
    """Servidor UDP para procesar el protocolo del ejercicio."""

    def __init__(
        self,
        host=HOST_POR_DEFECTO,
        puerto=PUERTO_POR_DEFECTO,
        rutas_ficheros=None,
    ):
        self.host = host
        self.puerto = puerto
        self.rutas_ficheros = rutas_ficheros or RUTAS_POR_DEFECTO
        self.busquedas_realizadas = 0
        self.mensajes_por_cliente = {}
        self.debe_terminar = False

    def procesar_mensaje(self, mensaje, direccion_cliente):
        self._contar_mensaje(direccion_cliente)

        partes = mensaje.split()
        if not partes:
            return RESPUESTA_ERROR

        comando = partes[0]

        if comando == COMANDO_BUSCAR:
            return self._procesar_buscar(partes)

        if comando == COMANDO_NUMERO:
            return self._procesar_numero(partes)

        if comando == COMANDO_SALIR:
            if not self._tiene_formato_sin_argumentos(partes):
                return RESPUESTA_ERROR
            return self._procesar_salir(direccion_cliente)

        return RESPUESTA_ERROR

    def ejecutar(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.bind((self.host, self.puerto))

            while not self.debe_terminar:
                datos, direccion_cliente = sock.recvfrom(TAMANO_BUFFER)
                mensaje = datos.decode("utf-8")
                respuesta = self.procesar_mensaje(mensaje, direccion_cliente)
                sock.sendto(respuesta.encode("utf-8"), direccion_cliente)

    def _contar_mensaje(self, direccion_cliente):
        self.mensajes_por_cliente[direccion_cliente] = (
            self.mensajes_por_cliente.get(direccion_cliente, 0) + 1
        )

    def _procesar_buscar(self, partes):
        if len(partes) != 2:
            return RESPUESTA_ERROR

        cadena = partes[1]
        lineas = self._buscar_coincidencias(cadena)
        self.busquedas_realizadas += 1

        if not lineas:
            return "0"

        return f"{len(lineas)}\n" + "\n".join(lineas)

    def _procesar_numero(self, partes):
        if not self._tiene_formato_sin_argumentos(partes):
            return RESPUESTA_ERROR

        return f"{RESPUESTA_OK} {self.busquedas_realizadas}"

    def _procesar_salir(self, direccion_cliente):
        mensajes = self.mensajes_por_cliente.get(direccion_cliente, 0)

        if mensajes < MINIMO_MENSAJES_SALIR:
            return (
                f"Aun solo se han enviado {mensajes} mensajes "
                f"de los {MINIMO_MENSAJES_SALIR} necesarios"
            )

        self.debe_terminar = True
        return RESPUESTA_OK

    def _tiene_formato_sin_argumentos(self, partes):
        return len(partes) == 1

    def _buscar_coincidencias(self, cadena):
        encontradas = []

        for ruta in self.rutas_ficheros:
            encontradas.extend(self._buscar_en_fichero(ruta, cadena))

        return encontradas

    def _buscar_en_fichero(self, ruta, cadena):
        try:
            with open(ruta, "r", encoding="utf-8") as fichero:
                return [
                    linea.rstrip("\n")
                    for linea in fichero
                    if cadena in linea.rstrip("\n")
                ]
        except OSError:
            return []
