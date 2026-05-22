# Plan de iteraciones

## 1. Requisitos confirmados

Se desarrollara un sistema cliente-servidor en Python, usando Programacion
Orientada a Objetos, sockets TCP/IP y pruebas con `unittest`.

El servidor:

- Escuchara en el puerto TCP `16063`.
- Usara por defecto el host `127.0.0.1`.
- Se ejecutara de forma continua.
- Aceptara conexiones de clientes.
- Recibira mensajes de texto.
- Respondera:
  - `FECHA`: fecha actual del sistema.
  - `HORA`: hora actual del sistema.
  - cualquier otro mensaje: `ERROR`.

El cliente:

- Se conectara automaticamente al servidor configurado en sus constructores.
- Permitira escribir mensajes por terminal de forma interactiva.
- Enviara como minimo 3 peticiones al servidor antes de poder cerrarse.
- Usara `SALIR` como orden local de cierre, sin enviarla al servidor.
- Si se escribe `SALIR` antes de 3 peticiones, mostrara:
  `Faltan x mensajes antes de poder cerrar el cliente`.
- Imprimira por salida estandar las respuestas del servidor o los errores.
- Terminara cuando se escriba `SALIR` despues de haber enviado al menos 3
  peticiones.

La aplicacion se lanzara desde `main.py` y la ejecucion se hara mediante
`make`.

## 2. Solucion tecnica de alto nivel

La solucion se organizara con una estructura simple y orientada a examen:

```text
simulacro-2026/
  main.py
  Makefile
  README.txt
  INSTALL.txt
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
    plan_de_iteraciones.md
```

Clases previstas:

- `ServidorTCP`: responsable de escuchar conexiones, procesar mensajes y
  responder segun el protocolo.
- `ClienteTCP`: responsable de conectar con el servidor, enviar mensajes,
  recibir respuestas y gestionar la regla local de minimo 3 peticiones.

El servidor tendra metodos separados para:

- procesar un mensaje individual;
- atender una conexion;
- arrancar el bucle continuo real.

Esta separacion permite probar el comportamiento sin bloquear los tests.

El cliente tendra metodos separados para:

- decidir si puede cerrar;
- calcular cuantos mensajes faltan;
- enviar una peticion al servidor;
- ejecutar el modo interactivo.

## 3. Estrategia TDD

El desarrollo seguira el ciclo:

```text
RED -> GREEN -> REFACTOR
```

Cada iteracion tendra tres entregas previstas:

- `Test n <ambito>`: pruebas en rojo.
- `Test n <ambito> OK`: implementacion minima para dejar las pruebas en verde.
- `Refactor n <ambito>`: mejora interna sin cambiar comportamiento.

El refactor se tratara como entrega casi obligatoria. Solo se omitira si no
existe ninguna mejora interna razonable que realizar.

## 4. Iteracion 1: Servidor

### Objetivo

Implementar la funcionalidad propia del servidor TCP:

- configuracion por defecto de host y puerto;
- procesamiento de mensajes `FECHA`, `HORA` y mensajes invalidos;
- escucha TCP;
- aceptacion de conexiones;
- respuesta al cliente.

### Entrega: Test 1 Servidor

Archivo afectado:

- `tests/test_server.py`

Pruebas previstas:

- Verificar que el servidor usa por defecto host `127.0.0.1` y puerto `16063`.
- Verificar que `FECHA` devuelve una fecha valida del sistema.
- Verificar que `HORA` devuelve una hora valida del sistema.
- Verificar que cualquier mensaje no reconocido devuelve `ERROR`.
- Verificar mediante socket real que el servidor puede atender una conexion de
  prueba y devolver la respuesta esperada.

Estas pruebas deberan quedar en rojo porque `ServidorTCP` todavia no existira o
no tendra la funcionalidad implementada.

### Entrega: Test 1 Servidor OK

Archivos afectados:

- `src/__init__.py`
- `src/servidor.py`
- `main.py`, solo si es necesario para exponer el modo servidor.

Implementacion minima:

- Crear la clase `ServidorTCP`.
- Definir host y puerto por defecto en el constructor.
- Implementar el procesamiento de mensajes.
- Implementar atencion de una conexion con sockets TCP.
- Preparar un metodo de arranque continuo para uso real.

### Entrega: Refactor 1 Servidor

Archivos afectados:

- `src/servidor.py`

Refactor previsto:

- Revisar nombres de metodos y constantes.
- Separar mejor la logica de protocolo de la logica de sockets si aporta
  claridad.
- Eliminar duplicidades detectadas tras dejar los tests en verde.

No se modificaran pruebas en esta entrega.

## 5. Iteracion 2: Cliente

### Objetivo

Implementar la funcionalidad propia del cliente:

- conexion automatica al servidor;
- envio de mensajes;
- recepcion e impresion de respuestas;
- control local de `SALIR`;
- minimo de 3 peticiones antes de permitir el cierre.

### Entrega: Test 2 Cliente

Archivo afectado:

- `tests/test_client.py`

Pruebas previstas:

- Verificar que el cliente usa por defecto host `127.0.0.1` y puerto `16063`.
- Verificar que `SALIR` no puede cerrar el cliente antes de 3 peticiones.
- Verificar que el mensaje de cierre prematuro indica cuantos mensajes faltan.
- Verificar que `SALIR` puede cerrar el cliente tras 3 peticiones enviadas.
- Verificar con un servidor de prueba TCP que el cliente envia un mensaje y
  devuelve/imprime la respuesta recibida.
- Verificar que los errores de conexion se capturan y se muestran por salida
  estandar.

Estas pruebas deberan quedar en rojo porque `ClienteTCP` todavia no existira o
no tendra la funcionalidad implementada.

### Entrega: Test 2 Cliente OK

Archivos afectados:

- `src/cliente.py`
- `main.py`, para exponer el modo cliente interactivo.

Implementacion minima:

- Crear la clase `ClienteTCP`.
- Definir host y puerto por defecto en el constructor.
- Implementar el contador de peticiones enviadas.
- Implementar la regla local de `SALIR`.
- Implementar envio de una peticion mediante socket TCP.
- Implementar bucle interactivo leyendo desde terminal.
- Imprimir respuestas o errores por salida estandar.

### Entrega: Refactor 2 Cliente

Archivos afectados:

- `src/cliente.py`

Refactor previsto:

- Separar la gestion de entrada interactiva de la logica de envio si mejora la
  claridad.
- Revisar nombres y simplificar condiciones del control de cierre.
- Eliminar duplicidades en mensajes de error o salida.

No se modificaran pruebas en esta entrega.

## 6. Iteracion 3: Integracion cliente-servidor

### Objetivo

Validar el flujo completo con cliente y servidor reales comunicandose por TCP.

### Entrega: Test 3 Integracion

Archivo afectado:

- `tests/test_integracion.py`

Pruebas previstas:

- Arrancar un servidor real en un puerto de prueba.
- Usar un cliente real contra ese servidor.
- Verificar flujo completo para `FECHA`.
- Verificar flujo completo para `HORA`.
- Verificar flujo completo para un mensaje invalido y respuesta `ERROR`.
- Verificar una secuencia de al menos 3 peticiones reales.

Estas pruebas deberan quedar en rojo si falta algun ajuste de colaboracion entre
cliente y servidor.

### Entrega: Test 3 Integracion OK

Archivos afectados:

- `src/servidor.py`
- `src/cliente.py`
- `main.py`
- `Makefile`, si hiciera falta ajustar comandos.

Implementacion minima:

- Ajustar servidor y cliente para que colaboren correctamente en ejecucion real.
- Garantizar que los tests unitarios acumulados siguen en verde.
- Garantizar que las pruebas de integracion no bloquean y cierran sus recursos.

### Entrega: Refactor 3 Integracion

Archivos afectados:

- `src/servidor.py`
- `src/cliente.py`
- `main.py`
- `Makefile`, solo si mejora claridad de ejecucion.

Refactor previsto:

- Revisar la inicializacion desde `main.py`.
- Consolidar constantes compartidas si aporta claridad sin sobreingenieria.
- Mejorar cierre de sockets y limpieza de recursos.
- Revisar documentacion de comandos de ejecucion.

No se modificaran pruebas en esta entrega.

## 7. Documentacion final

Archivos afectados:

- `README.txt`
- `INSTALL.txt`

Contenido previsto:

- Descripcion general del sistema.
- Manual de usuario.
- Comandos `make install`, `make test`, `make run-server` y `make run-client`.
- Ejemplos de uso.
- Dependencias necesarias.
- Preparacion del entorno virtual.

## 8. Riesgos y decisiones

Riesgos principales:

- Evitar bloqueos en tests que usen sockets reales.
- Liberar correctamente los puertos de prueba.
- No mezclar pruebas unitarias e integracion en la misma entrega.
- No adelantar funcionalidad de cliente durante la iteracion del servidor.

Decisiones:

- Se usara solo libreria estandar de Python salvo necesidad posterior.
- En tests se podran usar puertos de prueba dinamicos o auxiliares para evitar
  conflictos con el puerto real `16063`.
- El puerto real `16063` se mantendra en los constructores por defecto de las
  clases de produccion.
- `SALIR` sera una orden local del cliente y nunca se enviara al servidor.
