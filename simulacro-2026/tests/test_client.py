import io
import socket
import threading
import unittest
from contextlib import redirect_stdout


class TestClienteTCP(unittest.TestCase):
    """Pruebas unitarias de la Iteracion 2: Cliente."""

    def crear_cliente(self, *args, **kwargs):
        from src.cliente import ClienteTCP

        return ClienteTCP(*args, **kwargs)

    def test_iteracion_2_cliente_configuracion_por_defecto(self):
        """
        Iteracion 2 - Requisito: el cliente usa host local y puerto 16063 por
        defecto, definidos en el constructor.
        """
        cliente = self.crear_cliente()

        self.assertEqual("127.0.0.1", cliente.host)
        self.assertEqual(16063, cliente.puerto)

    def test_iteracion_2_cliente_no_sale_antes_de_tres_peticiones(self):
        """
        Iteracion 2 - Requisito: SALIR es una orden local y no permite cerrar
        antes de haber enviado 3 peticiones.
        """
        cliente = self.crear_cliente()

        respuesta = cliente.procesar_entrada("SALIR")

        self.assertEqual("Faltan 3 mensajes antes de poder cerrar el cliente", respuesta)
        self.assertTrue(cliente.activo)
        self.assertEqual(0, cliente.peticiones_enviadas)

    def test_iteracion_2_cliente_informa_cuantos_mensajes_faltan(self):
        """
        Iteracion 2 - Requisito: si se intenta salir antes del minimo, el
        cliente indica cuantos mensajes faltan.
        """
        cliente = self.crear_cliente()
        cliente.peticiones_enviadas = 2

        respuesta = cliente.procesar_entrada("SALIR")

        self.assertEqual("Faltan 1 mensajes antes de poder cerrar el cliente", respuesta)
        self.assertTrue(cliente.activo)

    def test_iteracion_2_cliente_sale_despues_de_tres_peticiones(self):
        """
        Iteracion 2 - Requisito: SALIR permite terminar el cliente cuando ya se
        han enviado al menos 3 peticiones.
        """
        cliente = self.crear_cliente()
        cliente.peticiones_enviadas = 3

        respuesta = cliente.procesar_entrada("SALIR")

        self.assertIsNone(respuesta)
        self.assertFalse(cliente.activo)

    def test_iteracion_2_cliente_envia_mensaje_y_recibe_respuesta_tcp_real(self):
        """
        Iteracion 2 - Requisito: el cliente se conecta al servidor configurado,
        envia un mensaje y recibe la respuesta por TCP.
        """
        mensaje_recibido = []
        puerto = self._arrancar_servidor_prueba("RESPUESTA\n", mensaje_recibido)
        cliente = self.crear_cliente(puerto=puerto)

        respuesta = cliente.enviar_peticion("FECHA")

        self.assertEqual("FECHA", mensaje_recibido[0])
        self.assertEqual("RESPUESTA", respuesta)
        self.assertEqual(1, cliente.peticiones_enviadas)

    def test_iteracion_2_cliente_imprime_errores_de_conexion(self):
        """
        Iteracion 2 - Requisito: el cliente imprime por salida estandar los
        errores que se produzcan al comunicarse con el servidor.
        """
        cliente = self.crear_cliente(puerto=self._puerto_libre_sin_servidor())
        salida = io.StringIO()

        with redirect_stdout(salida):
            respuesta = cliente.enviar_peticion("FECHA")

        self.assertIsNone(respuesta)
        self.assertIn("ERROR", salida.getvalue())
        self.assertEqual(0, cliente.peticiones_enviadas)

    def _arrancar_servidor_prueba(self, respuesta, mensajes_recibidos):
        servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        servidor.bind(("127.0.0.1", 0))
        servidor.listen(1)
        puerto = servidor.getsockname()[1]

        def atender():
            with servidor:
                conexion, _ = servidor.accept()
                with conexion:
                    datos = conexion.recv(1024).decode("utf-8").strip()
                    mensajes_recibidos.append(datos)
                    conexion.sendall(respuesta.encode("utf-8"))

        threading.Thread(target=atender, daemon=True).start()
        return puerto

    def _puerto_libre_sin_servidor(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as temporal:
            temporal.bind(("127.0.0.1", 0))
            return temporal.getsockname()[1]
