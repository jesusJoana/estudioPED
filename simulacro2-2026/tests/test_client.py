import io
import socket
import threading
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from src.cliente import ClienteUDP


class ServidorUDPPrueba:
    """Servidor UDP minimo para probar la responsabilidad del cliente."""

    def __init__(self, respuesta="OK"):
        self.respuesta = respuesta
        self.mensajes_recibidos = []
        self.puerto = 0
        self._activo = False

    def iniciar(self, max_mensajes=1):
        self._activo = True
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as servidor:
            servidor.bind(("127.0.0.1", 0))
            servidor.settimeout(0.2)
            self.puerto = servidor.getsockname()[1]
            recibidos = 0

            while self._activo and recibidos < max_mensajes:
                try:
                    datos, direccion = servidor.recvfrom(1024)
                except socket.timeout:
                    continue

                self.mensajes_recibidos.append(datos.decode("utf-8"))
                servidor.sendto(self.respuesta.encode("utf-8"), direccion)
                recibidos += 1

    def detener(self):
        self._activo = False


class TestClienteUDP(unittest.TestCase):
    """Pruebas unitarias de la Iteracion 2: Cliente."""

    def test_iteracion_2_envia_mensaje_y_recibe_respuesta_udp(self):
        """
        Iteracion 2 - Cliente.
        Requisito: el cliente envia un mensaje UDP al servidor configurado y
        devuelve la respuesta recibida.
        """
        servidor, hilo = self._arrancar_servidor_prueba(respuesta="RESPUESTA")
        cliente = ClienteUDP(host_servidor="127.0.0.1", puerto=servidor.puerto)

        try:
            respuesta = cliente.enviar_mensaje("FECHA")
        finally:
            servidor.detener()
            hilo.join(timeout=1)

        self.assertEqual("RESPUESTA", respuesta)
        self.assertEqual(["FECHA"], servidor.mensajes_recibidos)

    def test_iteracion_2_muestra_respuesta_por_salida_estandar(self):
        """
        Iteracion 2 - Cliente.
        Requisito: el cliente imprime en salida estandar las respuestas del
        servidor.
        """
        cliente = ClienteUDP()

        with patch.object(cliente, "enviar_mensaje", return_value="23/05/2026"):
            salida = io.StringIO()
            with redirect_stdout(salida):
                cliente.procesar_entrada("FECHA")

        self.assertIn("23/05/2026", salida.getvalue())

    def test_iteracion_2_salir_no_se_envia_al_servidor(self):
        """
        Iteracion 2 - Cliente.
        Requisito: SALIR es una orden local del cliente y no debe enviarse por
        UDP al servidor.
        """
        cliente = ClienteUDP()
        cliente.mensajes_enviados = 3

        with patch.object(cliente, "enviar_mensaje") as enviar_mensaje:
            cliente.procesar_entrada("SALIR")

        enviar_mensaje.assert_not_called()

    def test_iteracion_2_no_permite_salir_antes_de_tres_mensajes(self):
        """
        Iteracion 2 - Cliente.
        Requisito: si el usuario escribe SALIR antes de enviar 3 mensajes
        reales, el cliente lo impide y avisa por salida estandar.
        """
        cliente = ClienteUDP()
        cliente.mensajes_enviados = 2

        salida = io.StringIO()
        with redirect_stdout(salida):
            debe_continuar = cliente.procesar_entrada("SALIR")

        self.assertTrue(debe_continuar)
        self.assertIn("Aun no es posible", salida.getvalue())

    def test_iteracion_2_permite_salir_tras_tres_mensajes(self):
        """
        Iteracion 2 - Cliente.
        Requisito: tras enviar al menos 3 mensajes reales, SALIR finaliza el
        bucle interactivo del cliente.
        """
        cliente = ClienteUDP()
        cliente.mensajes_enviados = 3

        debe_continuar = cliente.procesar_entrada("SALIR")

        self.assertFalse(debe_continuar)

    def test_iteracion_2_contabiliza_solo_mensajes_enviados_al_servidor(self):
        """
        Iteracion 2 - Cliente.
        Requisito: el contador aumenta con mensajes enviados al servidor, pero
        no con la orden local SALIR.
        """
        cliente = ClienteUDP()

        with patch.object(cliente, "enviar_mensaje", return_value="ERROR"):
            cliente.procesar_entrada("HOLA")
            cliente.procesar_entrada("SALIR")

        self.assertEqual(1, cliente.mensajes_enviados)

    def test_iteracion_2_informa_error_de_comunicacion(self):
        """
        Iteracion 2 - Cliente.
        Requisito: el cliente informa por salida estandar de errores de
        comunicacion, por ejemplo timeout.
        """
        cliente = ClienteUDP(host_servidor="127.0.0.1", puerto=9, timeout=0.1)

        salida = io.StringIO()
        with redirect_stdout(salida):
            respuesta = cliente.enviar_mensaje("FECHA")

        self.assertIsNone(respuesta)
        self.assertIn("Error de comunicacion", salida.getvalue())

    def _arrancar_servidor_prueba(self, respuesta):
        servidor = ServidorUDPPrueba(respuesta=respuesta)
        hilo = threading.Thread(target=servidor.iniciar, daemon=True)
        hilo.start()

        for _ in range(100):
            if servidor.puerto != 0:
                return servidor, hilo

        servidor.detener()
        self.fail("El servidor UDP de prueba no quedo listo")


if __name__ == "__main__":
    unittest.main()
