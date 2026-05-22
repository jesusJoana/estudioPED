import socket


ORDEN_SALIR = "SALIR"
MINIMO_PETICIONES = 3
TAM_BUFFER = 1024


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
            with socket.create_connection((self.host, self.puerto), timeout=2) as cliente:
                cliente.sendall((mensaje + "\n").encode("utf-8"))
                respuesta = cliente.recv(TAM_BUFFER).decode("utf-8").strip()
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
        faltan = MINIMO_PETICIONES - self.peticiones_enviadas

        if faltan > 0:
            return f"Faltan {faltan} mensajes antes de poder cerrar el cliente"

        self.activo = False
        return None
