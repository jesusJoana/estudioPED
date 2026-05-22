import socket


ORDEN_SALIR = "SALIR"
MINIMO_PETICIONES = 3
TAM_BUFFER = 1024
TIMEOUT_CONEXION = 2
CODIFICACION = "utf-8"


class ClienteTCP:
    """Cliente TCP interactivo para enviar peticiones al servidor."""

    def __init__(self, host="127.0.0.1", puerto=16063):
        self.host = host
        self.puerto = puerto
        self.peticiones_enviadas = 0
        self.activo = True

    def procesar_entrada(self, mensaje):
        """Procesa una entrada local del usuario."""
        mensaje = mensaje.strip()

        if mensaje == ORDEN_SALIR:
            return self._procesar_salida()

        return self.enviar_peticion(mensaje)

    def enviar_peticion(self, mensaje):
        """Envia una peticion TCP al servidor y devuelve la respuesta."""
        try:
            with self._abrir_conexion() as cliente:
                cliente.sendall(self._codificar_mensaje(mensaje))
                respuesta = self._recibir_respuesta(cliente)
        except OSError as error:
            print(f"ERROR: {error}")
            return None

        self.peticiones_enviadas += 1
        return respuesta

    def ejecutar(self):
        """Ejecuta el cliente en modo interactivo por terminal."""
        while self.activo:
            try:
                mensaje = input("> ")
            except EOFError:
                break

            respuesta = self.procesar_entrada(mensaje)
            if respuesta is not None:
                print(respuesta)

    def _procesar_salida(self):
        """Aplica la regla de minimo de peticiones antes de cerrar."""
        faltan = self._peticiones_pendientes()

        if faltan > 0:
            return f"Faltan {faltan} mensajes antes de poder cerrar el cliente"

        self.activo = False
        return None

    def _abrir_conexion(self):
        """Crea una conexion TCP con el servidor configurado."""
        return socket.create_connection((self.host, self.puerto), timeout=TIMEOUT_CONEXION)

    def _codificar_mensaje(self, mensaje):
        """Prepara el mensaje para enviarlo por TCP."""
        return (mensaje + "\n").encode(CODIFICACION)

    def _recibir_respuesta(self, cliente):
        """Lee y decodifica la respuesta del servidor."""
        return cliente.recv(TAM_BUFFER).decode(CODIFICACION).strip()

    def _peticiones_pendientes(self):
        """Calcula cuantas peticiones faltan para poder salir."""
        return MINIMO_PETICIONES - self.peticiones_enviadas
