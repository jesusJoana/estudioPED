import io
import socket
import threading
import unittest

from src.cliente import ClienteUDP


class ServidorUDPDePrueba:
    """Servidor UDP minimo para probar la clase cliente."""

    def __init__(self, respuestas=None, responder=True):
        self.respuestas = list(respuestas or [])
        self.total_respuestas = len(self.respuestas)
        self.responder = responder
        self.mensajes_recibidos = []
        self._listo = threading.Event()
        self._hilo = threading.Thread(target=self._ejecutar, daemon=True)

    def iniciar(self):
        self._hilo.start()
        self._listo.wait(timeout=1)

    def esperar_fin(self):
        self._hilo.join(timeout=1)

    @property
    def puerto(self):
        return self._puerto

    def _ejecutar(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.bind(("127.0.0.1", 0))
            sock.settimeout(0.5)
            self._puerto = sock.getsockname()[1]
            self._listo.set()

            while len(self.mensajes_recibidos) < max(1, self.total_respuestas):
                try:
                    datos, direccion = sock.recvfrom(65535)
                except socket.timeout:
                    break

                mensaje = datos.decode("utf-8")
                self.mensajes_recibidos.append(mensaje)

                if self.responder and self.respuestas:
                    respuesta = self.respuestas.pop(0)
                    sock.sendto(respuesta.encode("utf-8"), direccion)


class TestClienteUDP(unittest.TestCase):
    """Pruebas unitarias de la Iteracion 2: Cliente."""

    def test_cliente_envia_mensaje_udp_y_recibe_respuesta(self):
        """Iteracion 2: el cliente envia un datagrama UDP y recibe respuesta."""
        servidor = ServidorUDPDePrueba(respuestas=["OK 0"])
        servidor.iniciar()
        cliente = ClienteUDP(host="127.0.0.1", puerto=servidor.puerto, timeout=0.5)

        respuesta = cliente.enviar_mensaje("NUMERO")
        cliente.cerrar()
        servidor.esperar_fin()

        self.assertEqual(respuesta, "OK 0")
        self.assertEqual(servidor.mensajes_recibidos, ["NUMERO"])

    def test_cliente_imprime_respuesta_recibida(self):
        """Iteracion 2: el cliente imprime en salida estandar la respuesta."""
        servidor = ServidorUDPDePrueba(respuestas=["OK 1"])
        servidor.iniciar()
        cliente = ClienteUDP(host="127.0.0.1", puerto=servidor.puerto, timeout=0.5)
        salida = io.StringIO()

        cliente.ejecutar_mensajes(["NUMERO"], salida=salida)
        cliente.cerrar()
        servidor.esperar_fin()

        self.assertIn("OK 1", salida.getvalue())

    def test_cliente_procesa_secuencia_de_al_menos_tres_mensajes(self):
        """Iteracion 2: el cliente puede enviar una secuencia de 3 mensajes."""
        servidor = ServidorUDPDePrueba(respuestas=["1\nroot", "OK 1", "OK"])
        servidor.iniciar()
        cliente = ClienteUDP(host="127.0.0.1", puerto=servidor.puerto, timeout=0.5)
        salida = io.StringIO()

        cliente.ejecutar_mensajes(["BUSCAR root", "NUMERO", "SALIR"], salida=salida)
        cliente.cerrar()
        servidor.esperar_fin()

        self.assertEqual(servidor.mensajes_recibidos, ["BUSCAR root", "NUMERO", "SALIR"])
        self.assertIn("1\nroot", salida.getvalue())
        self.assertIn("OK 1", salida.getvalue())
        self.assertIn("OK", salida.getvalue())

    def test_cliente_termina_tras_recibir_ok_a_salir(self):
        """Iteracion 2: tras SALIR con OK no envia mas mensajes."""
        servidor = ServidorUDPDePrueba(respuestas=["OK 0", "0", "OK"])
        servidor.iniciar()
        cliente = ClienteUDP(host="127.0.0.1", puerto=servidor.puerto, timeout=0.5)
        salida = io.StringIO()

        cliente.ejecutar_mensajes(
            ["NUMERO", "BUSCAR inexistente", "SALIR", "NUMERO"],
            salida=salida,
        )
        cliente.cerrar()
        servidor.esperar_fin()

        self.assertEqual(servidor.mensajes_recibidos, ["NUMERO", "BUSCAR inexistente", "SALIR"])

    def test_cliente_interactivo_no_termina_si_salir_no_recibe_ok(self):
        """Iteracion 2: SALIR no cierra el cliente hasta recibir OK del servidor."""
        servidor = ServidorUDPDePrueba(
            respuestas=[
                "Aun solo se han enviado 1 mensajes de los 3 necesarios",
                "OK 0",
                "OK",
            ]
        )
        servidor.iniciar()
        cliente = ClienteUDP(host="127.0.0.1", puerto=servidor.puerto, timeout=0.5)
        entrada = io.StringIO("SALIR\nNUMERO\nSALIR\nNUMERO\n")
        salida = io.StringIO()

        cliente.ejecutar_interactivo(entrada=entrada, salida=salida)
        cliente.cerrar()
        servidor.esperar_fin()

        self.assertEqual(servidor.mensajes_recibidos, ["SALIR", "NUMERO", "SALIR"])

    def test_cliente_imprime_error_si_no_recibe_respuesta(self):
        """Iteracion 2: el cliente informa de error si el servidor no responde."""
        servidor = ServidorUDPDePrueba(responder=False)
        servidor.iniciar()
        cliente = ClienteUDP(host="127.0.0.1", puerto=servidor.puerto, timeout=0.1)
        salida = io.StringIO()

        cliente.ejecutar_mensajes(["NUMERO"], salida=salida)
        cliente.cerrar()
        servidor.esperar_fin()

        self.assertIn("ERROR", salida.getvalue())

    def test_cliente_cierra_socket_correctamente(self):
        """Iteracion 2: el cliente cierra correctamente su socket UDP."""
        servidor = ServidorUDPDePrueba(respuestas=["OK 0"])
        servidor.iniciar()
        cliente = ClienteUDP(host="127.0.0.1", puerto=servidor.puerto, timeout=0.5)

        cliente.enviar_mensaje("NUMERO")
        cliente.cerrar()
        servidor.esperar_fin()

        self.assertTrue(cliente.esta_cerrado)

    def test_cliente_modificado_parsea_direccion_completa(self):
        """Iteracion 5: el cliente parsea una direccion completa host:puerto."""
        host, puerto = ClienteUDP.parsear_direccion_servidor("127.0.0.1:16063")

        self.assertEqual(host, "127.0.0.1")
        self.assertEqual(puerto, 16063)

    def test_cliente_modificado_rechaza_direccion_mal_formateada(self):
        """Iteracion 5: el cliente rechaza direcciones completas invalidas."""
        direcciones_invalidas = [
            "",
            "127.0.0.1",
            "127.0.0.1:",
            ":16063",
            "127.0.0.1:abc",
            "127.0.0.1:0",
            "127.0.0.1:70000",
            "127.0.0.1:16063:extra",
        ]

        for direccion in direcciones_invalidas:
            with self.subTest(direccion=direccion):
                with self.assertRaises(ValueError):
                    ClienteUDP.parsear_direccion_servidor(direccion)

    def test_cliente_modificado_solicita_direccion_completa(self):
        """Iteracion 5: el cliente pregunta al usuario por la direccion del servidor."""
        entrada = io.StringIO("127.0.0.1:16063\n")
        salida = io.StringIO()

        host, puerto = ClienteUDP.pedir_direccion_servidor(entrada=entrada, salida=salida)

        self.assertEqual(host, "127.0.0.1")
        self.assertEqual(puerto, 16063)
        self.assertIn("Direccion completa del servidor", salida.getvalue())

    def test_cliente_modificado_informa_error_si_no_comunica_con_servidor(self):
        """Iteracion 5: el cliente imprime error si no consigue comunicarse."""
        puerto_libre = self._obtener_puerto_libre()
        entrada = io.StringIO(f"127.0.0.1:{puerto_libre}\nNUMERO\nNUMERO\nSALIR\n")
        salida = io.StringIO()

        ClienteUDP.ejecutar_desde_terminal(entrada=entrada, salida=salida, timeout=0.1)

        self.assertIn("ERROR", salida.getvalue())

    def test_cliente_modificado_con_direccion_correcta_mantiene_flujo(self):
        """Iteracion 5: con direccion correcta, el cliente mantiene el flujo normal."""
        servidor = ServidorUDPDePrueba(respuestas=["OK 0", "0", "OK"])
        servidor.iniciar()
        entrada = io.StringIO(f"127.0.0.1:{servidor.puerto}\nNUMERO\nBUSCAR nada\nSALIR\n")
        salida = io.StringIO()

        ClienteUDP.ejecutar_desde_terminal(entrada=entrada, salida=salida, timeout=0.5)
        servidor.esperar_fin()

        self.assertEqual(servidor.mensajes_recibidos, ["NUMERO", "BUSCAR nada", "SALIR"])
        self.assertIn("OK 0", salida.getvalue())

    def _obtener_puerto_libre(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.bind(("127.0.0.1", 0))
            return sock.getsockname()[1]


if __name__ == "__main__":
    unittest.main()
