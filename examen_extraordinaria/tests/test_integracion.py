import io
import os
import socket
import tempfile
import threading
import time
import unittest

from src.cliente import ClienteUDP
from src.servidor import ServidorUDP


def obtener_puerto_libre():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


class TestIntegracionClienteServidor(unittest.TestCase):
    """Pruebas de la Iteracion 3: Integracion cliente-servidor."""

    def setUp(self):
        self.directorio = tempfile.TemporaryDirectory()
        self.services = os.path.join(self.directorio.name, "services")
        self.passwd = os.path.join(self.directorio.name, "passwd")

        with open(self.services, "w", encoding="utf-8") as fichero:
            fichero.write("ssh 22/tcp # SSH Remote Login Protocol\n")
            fichero.write("http 80/tcp # World Wide Web\n")

        with open(self.passwd, "w", encoding="utf-8") as fichero:
            fichero.write("root:x:0:0:root:/root:/bin/bash\n")
            fichero.write("usuario:x:1000:1000:usuario:/home/usuario:/bin/bash\n")

        self.puerto = obtener_puerto_libre()
        self.servidor = ServidorUDP(
            host="127.0.0.1",
            puerto=self.puerto,
            rutas_ficheros=[self.services, self.passwd],
        )
        self.hilo_servidor = threading.Thread(target=self.servidor.ejecutar, daemon=True)
        self.hilo_servidor.start()
        time.sleep(0.05)

    def tearDown(self):
        if not self.servidor.debe_terminar:
            self._detener_servidor()
        self.hilo_servidor.join(timeout=1)
        self.directorio.cleanup()

    def test_cliente_y_servidor_intercambian_buscar_numero_y_salir(self):
        """Iteracion 3: cliente y servidor reales completan BUSCAR, NUMERO y SALIR."""
        cliente = ClienteUDP(host="127.0.0.1", puerto=self.puerto, timeout=0.5)
        salida = io.StringIO()

        cliente.ejecutar_mensajes(["BUSCAR root", "NUMERO", "SALIR"], salida=salida)
        cliente.cerrar()
        self.hilo_servidor.join(timeout=1)

        texto = salida.getvalue()
        self.assertIn("1\nroot:x:0:0:root:/root:/bin/bash", texto)
        self.assertIn("OK 1", texto)
        self.assertIn("OK", texto)
        self.assertTrue(self.servidor.debe_terminar)
        self.assertFalse(self.hilo_servidor.is_alive())

    def test_salir_antes_del_tercer_mensaje_no_detiene_servidor(self):
        """Iteracion 3: SALIR antes del tercer mensaje no detiene el servidor real."""
        cliente = ClienteUDP(host="127.0.0.1", puerto=self.puerto, timeout=0.5)

        respuesta = cliente.enviar_mensaje("SALIR")

        self.assertEqual(
            respuesta,
            "Aun solo se han enviado 1 mensajes de los 3 necesarios",
        )
        self.assertFalse(self.servidor.debe_terminar)
        self.assertTrue(self.hilo_servidor.is_alive())

        cliente.enviar_mensaje("NUMERO")
        respuesta_final = cliente.enviar_mensaje("SALIR")
        cliente.cerrar()
        self.hilo_servidor.join(timeout=1)

        self.assertEqual(respuesta_final, "OK")
        self.assertTrue(self.servidor.debe_terminar)

    def test_cliente_interactivo_no_debe_finalizar_con_menos_de_tres_mensajes(self):
        """Iteracion 3: el cliente interactivo debe exigir un minimo de 3 mensajes."""
        cliente = ClienteUDP(host="127.0.0.1", puerto=self.puerto, timeout=0.5)
        entrada = io.StringIO("NUMERO\n")
        salida = io.StringIO()

        cliente.ejecutar_interactivo(entrada=entrada, salida=salida)
        cliente.cerrar()

        mensajes = sum(self.servidor.mensajes_por_cliente.values())
        self.assertGreaterEqual(mensajes, 3)

    def test_mensaje_invalido_devuelve_error_en_integracion(self):
        """Iteracion 3: un mensaje invalido devuelve ERROR entre cliente y servidor reales."""
        cliente = ClienteUDP(host="127.0.0.1", puerto=self.puerto, timeout=0.5)

        respuesta = cliente.enviar_mensaje("HOLA")
        cliente.cerrar()

        self.assertEqual(respuesta, "ERROR")

    def _detener_servidor(self):
        cliente = ClienteUDP(host="127.0.0.1", puerto=self.puerto, timeout=0.5)
        try:
            cliente.enviar_mensaje("NUMERO")
            cliente.enviar_mensaje("NUMERO")
            cliente.enviar_mensaje("SALIR")
        finally:
            cliente.cerrar()


if __name__ == "__main__":
    unittest.main()
