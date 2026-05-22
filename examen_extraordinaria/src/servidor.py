import socket


class ServidorUDP:
    """Servidor UDP para procesar el protocolo del ejercicio."""

    def __init__(self, host="127.0.0.1", puerto=16063, rutas_ficheros=None):
        self.host = host
        self.puerto = puerto
        self.rutas_ficheros = rutas_ficheros or ["/etc/services", "/etc/passwd"]
        self.busquedas_realizadas = 0
        self.mensajes_por_cliente = {}
        self.debe_terminar = False

    def procesar_mensaje(self, mensaje, direccion_cliente):
        self._contar_mensaje(direccion_cliente)

        partes = mensaje.split()
        if not partes:
            return "ERROR"

        comando = partes[0]

        if comando == "BUSCAR":
            return self._procesar_buscar(partes)

        if comando == "NUMERO":
            if len(partes) != 1:
                return "ERROR"
            return f"OK {self.busquedas_realizadas}"

        if comando == "SALIR":
            if len(partes) != 1:
                return "ERROR"
            return self._procesar_salir(direccion_cliente)

        return "ERROR"

    def ejecutar(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.bind((self.host, self.puerto))

            while not self.debe_terminar:
                datos, direccion_cliente = sock.recvfrom(65535)
                mensaje = datos.decode("utf-8")
                respuesta = self.procesar_mensaje(mensaje, direccion_cliente)
                sock.sendto(respuesta.encode("utf-8"), direccion_cliente)

    def _contar_mensaje(self, direccion_cliente):
        self.mensajes_por_cliente[direccion_cliente] = (
            self.mensajes_por_cliente.get(direccion_cliente, 0) + 1
        )

    def _procesar_buscar(self, partes):
        if len(partes) != 2:
            return "ERROR"

        cadena = partes[1]
        lineas = self._buscar_lineas(cadena)
        self.busquedas_realizadas += 1

        if not lineas:
            return "0"

        return f"{len(lineas)}\n" + "\n".join(lineas)

    def _procesar_salir(self, direccion_cliente):
        mensajes = self.mensajes_por_cliente.get(direccion_cliente, 0)

        if mensajes < 3:
            return f"Aun solo se han enviado {mensajes} mensajes de los 3 necesarios"

        self.debe_terminar = True
        return "OK"

    def _buscar_lineas(self, cadena):
        encontradas = []

        for ruta in self.rutas_ficheros:
            try:
                with open(ruta, "r", encoding="utf-8") as fichero:
                    for linea in fichero:
                        linea_limpia = linea.rstrip("\n")
                        if cadena in linea_limpia:
                            encontradas.append(linea_limpia)
            except OSError:
                continue

        return encontradas
