# Integración pendiente del formulario existente

## Material necesario

Facilitar el **código fuente del addon instalado que declara
`/portal/production/new`**, con su `__manifest__.py`, sus imports, controladores,
plantillas QWeb y lógica de creación de órdenes (incluidos servicios/modelos
invocados). Si la vista se cambió mediante el editor/Studio, facilitar también su
arquitectura heredada. Los nombres de esos archivos e identificadores no pueden
determinarse con el repositorio vacío.

También se necesita confirmar la versión técnica de Odoo en el servidor,
el tema/encabezado activo, los registros del menú y las personalizaciones de
seguridad de usuarios portal/sucursal. Una instancia de pruebas autorizada es
necesaria para comprobar el flujo completo. No hacen falta contraseñas en chat.

## Procedimiento al disponer del código

1. Localizar la ruta GET y **todas** las rutas POST/JSON/RPC que reciben o crean
   las órdenes. Identificar la clase original, método real, `auth`, métodos HTTP,
   tipo de ruta, CSRF, plantilla, nombre HTML y campo/modelo de la fecha. Rastrear
   el botón «Crear Orden(es)» y cualquier creación múltiple. Revisar asociaciones
   y restricciones por empresa/sucursal antes de cambiar nada.
2. Crear una extensión que dependa del nombre técnico **real** del addon original
   (preferentemente un segundo addon de integración, para que el presente no
   dependa de componentes imaginados). Heredar la clase original y volver a
   decorar los métodos reales con `auth='user'`, conservando las demás opciones
   apropiadas de su ruta. No registrar un controlador independiente que compita
   por la misma URL. Mantener CSRF en los formularios HTTP; investigar cualquier
   ruta de guardado sin protección. No introducir `sudo()` ni ampliar permisos.
3. En la apertura de un formulario **nuevo**, llamar a
   `new_order_date_values()` e incorporar sus valores al contexto QWeb real.
   Heredar la plantilla identificada para asignar `value` y `min` al input real
   de tipo `date`; mantenerlo habilitado y obligatorio. No aplicar este cambio
   a consultas/ediciones históricas. No calcular «hoy» en el navegador.
4. En el receptor efectivo, antes de **cualquier escritura o creación**, llamar
   a `validate_new_order_date(valor_real)` y utilizar la fecha validada en los
   valores enviados al modelo. En creación múltiple validar todo el pedido
   antes de crear la primera orden. No basta validar la ruta GET ni interceptar
   solo una parte de las rutas de guardado.
5. Capturar `InvalidOrderDate` antes de escribir. Mostrar su mensaje mediante el
   mecanismo de errores del formulario original, conservar empresa, sucursal,
   agrupador, productos y cantidades, y recalcular el mínimo Lima. No llamar a la
   creación en ese caso. Si un formulario quedó abierto hasta el día siguiente,
   rechazar la fecha que dejó de cumplir y permitir corregirla sin perder datos.
   El error debe escapar mediante QWeb; no insertar HTML recibido del cliente.
6. Conservar intacta la validación de empresa/sucursal/productos/cantidades y la
   creación original. No aplicar restricciones globales al modelo de producción:
   afectaría a otros flujos y a órdenes históricas sin necesidad.
7. Verificar que el login estándar redirige al formulario para visitantes y que
   las rutas de escritura también rechazan usuarios públicos. No añadir un login
   propio ni alterar contraseñas. Revisar cualquier ruta alternativa descubierta.

No se entregan clases, XML IDs, campos ni llamadas de creación ficticios. La
política de fechas entregada es una utilidad probada; **no es una validación
efectiva de las órdenes mientras el receptor real no la invoque**.
