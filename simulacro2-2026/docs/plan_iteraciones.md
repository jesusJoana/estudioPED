# Plan de iteraciones

## Proyecto

Sistema cliente-servidor mediante sockets UDP.

El servidor atendera peticiones en el puerto UDP `16063` y permanecera en
ejecucion continua. El cliente pedira al usuario la direccion del servidor,
enviara mensajes de forma iterativa por terminal y solo permitira finalizar con
`SALIR` cuando se hayan enviado como minimo 3 mensajes reales al servidor.

## Requisitos confirmados

- Lenguaje principal: Python.
- Paradigma: Programacion Orientada a Objetos.
- Comunicacion: sockets UDP.
- Puerto del servidor: `16063`.
- Host por defecto del servidor: `0.0.0.0`, para aceptar mensajes de cualquier
  cliente.
- Host por defecto del cliente para pruebas locales: `127.0.0.1`.
- Los valores fijos de host y puerto estaran definidos en los constructores de
  las clases de cliente y servidor.
- La aplicacion se lanzara desde `main.py`.
- La ejecucion de aplicacion y pruebas se hara mediante `make`.
- Las pruebas se implementaran con `unittest`.
- El servidor respondera:
  - `FECHA`: fecha actual del sistema.
  - `HORA`: hora actual del sistema.
  - cualquier otro mensaje: `ERROR`.
- El protocolo distingue mayusculas y minusculas:
  - `FECHA` funciona.
  - `HORA` funciona.
  - `fecha`, `hora`, `Fecha`, `Hora` devuelven `ERROR`.
- `SALIR` es una orden local del cliente, no un mensaje enviado al servidor.
- Si el usuario escribe `SALIR` antes de enviar 3 mensajes al servidor, el
  cliente lo impedira y mostrara un aviso.
- Si el usuario escribe `SALIR` despues de enviar al menos 3 mensajes reales, el
  cliente cerrara correctamente.
- El cliente mostrara por salida estandar las respuestas del servidor y las
  condiciones de error.

## Estructura prevista

```text
simulacro2-2026/
  main.py
  src/
    __init__.py
    servidor.py
    cliente.py
  tests/
    __init__.py
    test_server.py
    test_client.py
    test_integracion.py
  docs/
    plan_iteraciones.md
  README.txt
  INSTALL.txt
  Makefile
```

## Iteracion 1: Servidor

### Objetivo

Implementar la clase responsable del servidor UDP, capaz de recibir datagramas,
procesar mensajes y generar respuestas segun el protocolo definido.

### Entrega: Test 1 Servidor

Pruebas unitarias en `tests/test_server.py`.

Casos previstos:

- El servidor responde con una fecha valida al recibir `FECHA`.
- El servidor responde con una hora valida al recibir `HORA`.
- El servidor responde `ERROR` ante mensajes no reconocidos.
- El servidor distingue mayusculas y minusculas: `fecha` devuelve `ERROR`.
- El servidor puede atender mas de un mensaje sin finalizar.

Estas pruebas deberan quedar inicialmente en rojo.

### Entrega: Test 1 Servidor OK

Implementacion minima en `src/servidor.py`.

Estrategia:

- Crear una clase `ServidorUDP`.
- Definir host y puerto en el constructor.
- Implementar el procesamiento del mensaje en un metodo separado para facilitar
  pruebas.
- Usar socket UDP real para validar recepcion y respuesta.
- Permitir en pruebas ejecutar el servidor con un numero limitado de mensajes
  para evitar bloqueos.
- Mantener el modo real del servidor como ejecucion continua.

### Entrega: Refactor 1 Servidor

Refactor recomendado siempre que haya mejora interna razonable.

Posibles mejoras:

- Separar la logica de protocolo de la logica de socket si el codigo queda
  mezclado.
- Mejorar nombres de metodos y constantes.
- Centralizar formato de fecha y hora.
- Revisar cierre correcto del socket.

No se modificara el comportamiento observable ni se anadiran nuevos requisitos.

## Iteracion 2: Cliente

### Objetivo

Implementar la clase responsable del cliente UDP, capaz de pedir la direccion
del servidor, enviar mensajes introducidos por terminal y controlar la regla de
minimo 3 mensajes antes de permitir `SALIR`.

### Entrega: Test 2 Cliente

Pruebas unitarias en `tests/test_client.py`.

Casos previstos:

- El cliente envia un mensaje UDP al servidor configurado y recibe la respuesta.
- El cliente muestra la respuesta recibida por salida estandar.
- El cliente no envia `SALIR` al servidor.
- El cliente no permite finalizar con `SALIR` antes de haber enviado 3 mensajes
  reales.
- El cliente permite finalizar con `SALIR` tras haber enviado 3 mensajes reales.
- El cliente contabiliza solo mensajes enviados al servidor, no la orden local
  `SALIR`.
- El cliente informa de errores de comunicacion, por ejemplo timeout.

Estas pruebas deberan quedar inicialmente en rojo.

### Entrega: Test 2 Cliente OK

Implementacion minima en `src/cliente.py`.

Estrategia:

- Crear una clase `ClienteUDP`.
- Definir puerto por defecto en el constructor.
- Pedir la direccion del servidor desde el flujo interactivo.
- Implementar un metodo para enviar un mensaje y recibir respuesta.
- Implementar el bucle interactivo con contador de mensajes enviados.
- Tratar `SALIR` como orden local antes de enviar nada por UDP.
- Configurar timeout para evitar bloqueos indefinidos.

### Entrega: Refactor 2 Cliente

Refactor recomendado siempre que haya mejora interna razonable.

Posibles mejoras:

- Separar envio UDP y bucle interactivo.
- Mejorar mensajes al usuario.
- Extraer comprobacion de salida a un metodo pequeno.
- Revisar manejo y cierre del socket.

No se modificara el comportamiento observable ni se anadiran nuevos requisitos.

## Iteracion 3: Integracion cliente-servidor

### Objetivo

Validar el funcionamiento completo con cliente y servidor reales colaborando
mediante UDP.

### Entrega: Test 3 Integracion

Pruebas de integracion en `tests/test_integracion.py`.

Casos previstos:

- Cliente y servidor reales intercambian `FECHA` y el cliente recibe una fecha
  valida.
- Cliente y servidor reales intercambian `HORA` y el cliente recibe una hora
  valida.
- Cliente y servidor reales intercambian un mensaje desconocido y el cliente
  recibe `ERROR`.
- Flujo completo de cliente: tres mensajes reales y despues `SALIR`.
- El servidor sigue activo mientras atiende varios mensajes.

Estas pruebas deberan quedar inicialmente en rojo.

### Entrega: Test 3 Integracion OK

Implementacion minima para dejar en verde la integracion y todos los tests
acumulados.

Estrategia:

- Arrancar el servidor en un proceso o hilo controlado desde el test.
- Usar puertos de prueba cuando sea necesario para evitar conflictos.
- Usar timeouts para impedir bloqueos.
- Verificar el flujo extremo a extremo sin depender de intervencion manual.
- Completar `main.py` para lanzar servidor o cliente segun el modo indicado.
- Ajustar `Makefile` para ejecutar aplicacion y tests.

### Entrega: Refactor 3 Integracion

Refactor recomendado siempre que haya mejora interna razonable.

Posibles mejoras:

- Simplificar helpers de arranque/parada en tests.
- Revisar duplicidad entre pruebas unitarias e integracion.
- Mejorar documentacion interna de los tests.
- Ajustar nombres de objetivos del `Makefile`.

No se modificara el comportamiento observable ni se anadiran nuevos requisitos.

## Documentacion final

Al cerrar el desarrollo se generaran:

- `README.txt`, con descripcion, manual de usuario, instrucciones basicas de
  ejecucion, ejemplos de uso y explicacion funcional.
- `INSTALL.txt`, con instalacion, dependencias, preparacion del entorno,
  comandos de ejecucion y pasos para poner el sistema en funcionamiento.

## Riesgos y decisiones

- UDP no tiene conexion persistente ni garantia de entrega; se usaran timeouts
  en cliente y pruebas para evitar bloqueos.
- El servidor real sera continuo, pero en pruebas debera poder limitarse el
  numero de mensajes procesados.
- La comparacion de mensajes sera estricta: no se normalizara a mayusculas.
- `SALIR` se interpreta exclusivamente en el cliente.
- El refactor se realizara como entrega separada siempre que exista una mejora
  razonable sin alterar comportamiento.
