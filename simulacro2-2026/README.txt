README - Sistema cliente-servidor UDP
====================================

1. Descripcion general
----------------------

Este proyecto implementa un sistema cliente-servidor usando sockets UDP en
Python.

El servidor escucha de forma continua en el puerto UDP 16063 y responde a los
mensajes enviados por cualquier cliente.

Protocolo de mensajes:

- FECHA: el servidor responde con la fecha actual del sistema.
- HORA: el servidor responde con la hora actual del sistema.
- Cualquier otro mensaje: el servidor responde ERROR.

El protocolo distingue mayusculas y minusculas. Por tanto, FECHA y HORA son
validos, pero fecha, hora, Fecha u Hora devuelven ERROR.

El cliente pide al usuario la direccion del servidor, envia mensajes de forma
iterativa por terminal y muestra por salida estandar las respuestas recibidas.

La orden SALIR no se envia al servidor. Es una orden local del cliente para
finalizar. El cliente solo permite salir cuando ya se han enviado al menos 3
mensajes reales al servidor.

2. Estructura del proyecto
--------------------------

simulacro2-2026/
  main.py
  src/
    __init__.py
    cliente.py
    servidor.py
  tests/
    __init__.py
    test_client.py
    test_integracion.py
    test_server.py
  docs/
    plan_iteraciones.md
  README.txt
  INSTALL.txt
  Makefile

3. Ejecucion del servidor
-------------------------

Desde la carpeta del proyecto:

make run-server

Tambien se puede ejecutar con:

make server

El servidor queda escuchando en:

0.0.0.0:16063

Para detenerlo manualmente, usar Ctrl+C en la terminal donde se esta ejecutando.

4. Ejecucion del cliente
------------------------

En otra terminal, desde la carpeta del proyecto:

make run-client

Tambien se puede ejecutar con:

make client

El cliente pedira la direccion del servidor. Para pruebas en la misma maquina,
introducir:

127.0.0.1

Despues se podran escribir mensajes por terminal.

5. Ejemplo de uso
-----------------

Terminal 1:

make run-server

Terminal 2:

make run-client

Ejemplo de sesion del cliente:

Introduce la direccion del servidor: 127.0.0.1
Mensaje: FECHA
23/05/2026
Mensaje: HORA
18:42:10
Mensaje: fecha
ERROR
Mensaje: SALIR
Cliente finalizado correctamente.

Ejemplo de intento de salida antes de tiempo:

Introduce la direccion del servidor: 127.0.0.1
Mensaje: FECHA
23/05/2026
Mensaje: SALIR
Aun no es posible salir. Debes enviar al menos 3 mensajes al servidor.

6. Pruebas
----------

Las pruebas estan implementadas con unittest y se ejecutan con:

make test

La suite incluye:

- pruebas unitarias del servidor en tests/test_server.py;
- pruebas unitarias del cliente en tests/test_client.py;
- pruebas de integracion cliente-servidor en tests/test_integracion.py.

7. Decisiones tecnicas
----------------------

- Se usa UDP porque es el mecanismo indicado en el enunciado.
- El servidor usa host 0.0.0.0 para aceptar datagramas de cualquier cliente.
- El cliente usa por defecto el puerto 16063.
- El servidor real se ejecuta de forma continua.
- En pruebas, el servidor puede limitar el numero de mensajes para evitar
  bloqueos.
- SALIR se interpreta solo en el cliente y nunca se envia al servidor.
- No se normalizan mayusculas/minusculas para respetar el protocolo estricto.

