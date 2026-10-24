# Evidencia y matriz de aceptación

## Automatizado sin Odoo

Ejecutar desde la raíz: `python -m unittest discover -s tests -v`.

- Default y mínimo coinciden con mañana en Lima.
- Cambio de día a las 05:00 UTC; formulario abierto del día anterior.
- Fin de año y año bisiesto.
- Mañana y fechas posteriores aceptadas; hoy y anteriores rechazadas.
- Fechas ausentes, imposibles, datetime y entradas manipuladas rechazadas.
- XML válido, dependencias/IDs declarados y contrato de enlace/deduplicación.

También se prueba el controlador de la extensión con dobles del padre y de
Odoo: CSRF válido/inválido, fecha rechazada antes de delegar, preservación de los
parámetros y resultado del original. No representa una prueba de las rutas HTTP
reales, seguridad ORM ni instalación.

Resultado local: **20 pruebas ejecutadas, 20 aprobadas, ninguna omitida**.
También se comprobó sintaxis Python y que cada XPath coincide una sola vez en
su plantilla oficial de Odoo 19; las expresiones combinadas de QWeb compilan.
La comprobación XPath usó `lxml` disponible en la máquina, sin instalar paquetes.
No se ejecutó el motor QWeb de Odoo.

Fuente contrastada:
`https://raw.githubusercontent.com/odoo/odoo/19.0/addons/website/views/website_templates.xml`.
SHA-256 del archivo consultado:
`7618bf46eb9ba8d61969c0e1268724617cbee1848149e1fa94e9e972ad2d5040`.

## Pendiente en Odoo de pruebas, con el addon original y esta extensión

| Caso | Resultado requerido |
| --- | --- |
| Encabezado público y autenticado | «Realizar Pedido» visible, antes de «Contáctanos», sin duplicados |
| Anchos 375, 768 y 1440 px | Botón legible y accesible con teclado, menú móvil funcional |
| Tema y diferentes páginas web/portal | Granate y fuente correctos; no romper encabezados personalizados |
| Visitante abre botón o URL directa | Login estándar, sin contenido del formulario ni escrituras |
| Login correcto | Retorno directo al formulario |
| Usuario autorizado | Acceso directo y solo empresas/sucursales permitidas |
| Petición manipulada de otra sucursal | Rechazo por las restricciones originales |
| Formulario nuevo | Mañana Lima seleccionada; calendario habilitado y mínimo correcto |
| Elegir fecha futura | Se conserva y permite crear órdenes |
| Quitar `min` o cambiar fecha por HTTP | Hoy/pasado/formato inválido rechazados; cero órdenes creadas |
| Pedido múltiple inválido | Cero órdenes o efectos parciales |
| CSRF ausente/incorrecto y escritura pública | Rechazo sin órdenes creadas |
| Error de fecha | Mensaje claro y resto de selecciones/cantidades conservados |
| «Crear Orden(es)» válido | Mismas órdenes, asociaciones y cantidades que el flujo original |
| Consulta de órdenes históricas | Fechas intactas; nuevo mínimo no aplicado |

Automatizar estas pruebas contra las rutas/modelos reales cuando se obtengan.
Ejecutar únicamente en una base de pruebas: los casos de creación no deben usar
datos de producción. No se han ejecutado ni se consideran aprobados.

## Confirmación de fuentes recibidas

El XML real del ZIP contiene una sola plantilla `production_form` y un solo
input `date_order` en `portal_production_form`; el XPath de la extensión coincide
una vez. El controlador original declara ambas rutas con `auth='user'`; el
receptor es POST `jsonrpc` y el JS original envía `csrf_token`.
