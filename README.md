# ALVIÑA — Acceso web a pedidos

**Implementación parcial, sin despliegue. No está lista para habilitar pedidos en
producción.** El repositorio remoto inspeccionado no contiene commits ni código
del formulario. Se implementa lo verificable sin sustituir el flujo existente.

## Componentes entregados

- Addon `alvina_website_order_entry`, versión objetivo Odoo **19.0**.
- Dependencia real: `website`. No se presupone ningún módulo de producción.
- Herencia de `website.navbar_nav`: enlace «Realizar Pedido» a
  `/portal/production/new`, sin condición por sesión, como primer elemento del
  menú estándar (antes de «Contáctanos», no necesariamente justo a su lado).
  El menú estándar de escritorio y móvil utiliza esa plantilla en Odoo 19.
- Herencia de `website.submenu`: suprime entradas estándar con la misma ruta
  interna, incluyendo barra final, query y fragmento. No crea registros de menú.
- Estilo responsive, fuente heredada y granate provisional `#800020`, configurable
  mediante la variable CSS `--alvina-order-color` del tema.
- Política de fechas backend en `services/order_date.py`, sin acceso a datos:
  mañana en `America/Lima`, valores ISO de default/mínimo y rechazo de fechas
  ausentes, inválidas, actuales o pasadas. **Todavía no está conectada al formulario
  ni al guardado de órdenes.**

No se crean modelos, campos, permisos, controladores alternativos, autenticación,
JS ni cambios en órdenes históricas. El enlace directo no impone autenticación:
eso corresponde al controlador original, que aún falta.

## Inspección y límites

Se contrastaron los IDs y XPath con los archivos oficiales de Odoo en la rama
`19.0`: `addons/website/views/website_templates.xml` y
`addons/website/models/website_menu.py`. **La versión instalada en ALVIÑA no se
ha confirmado.** Los intentos de lectura de la web y del formulario fueron
bloqueados por el proxy del entorno (`403 Forbidden` al establecer el túnel).
No se intentó iniciar sesión, enviar pedidos ni cambiar producción.

Falta el código que identifica el módulo, clase/métodos de controlador, QWeb,
campo real de fecha, modelos creados y todas las rutas de recepción. Consultar
[docs/INTEGRATION.md](docs/INTEGRATION.md) para completar la integración segura.

El encabezado real podría estar personalizado. Los menús ajenos a las plantillas
estándar, enlaces absolutos al mismo formulario, botones adicionales del tema y
otros sitios de una base multisite requieren inspección. El addon afecta todos
los sitios que usan las plantillas estándar; no instalarlo en una base multisite
sin revisar ese alcance. No se afirma ausencia de duplicados fuera de ese menú.
Un nodo desplegable cuya URL sea la del formulario se suprime con sus hijos:
revisar la estructura real del menú antes de habilitarlo.

## Pruebas locales ejecutables

Python 3.12 y base IANA de zonas horarias del sistema, sin dependencias de pip:

```bash
cd /workspace/alvina_portal_pedidos
python -m unittest discover -s tests -v
```

Las pruebas comprueban la política de fechas, límites de Lima, fechas manipuladas
y contrato estático de las vistas. No prueban HTTP, renderizado real de QWeb,
CSRF, permisos, responsive visual ni creación de órdenes. La matriz pendiente
está en [docs/VALIDATION.md](docs/VALIDATION.md). No hay Odoo ni PostgreSQL en este
entorno; tampoco hay base de pruebas ni el módulo del formulario.

## Instalación / actualización en un servidor de pruebas

1. Obtener y revisar primero el módulo original y confirmar la versión. Completar
   la integración descrita en `docs/INTEGRATION.md` antes de habilitar el botón
   para usuarios finales. Utilizar una base de pruebas y datos anonimizados.
2. Copiar `alvina_website_order_entry` dentro de un directorio ya incluido en
   `addons_path` del servidor Odoo 19. No modificar el núcleo de Odoo.
3. Con el ejecutable y configuración reales del servidor, instalar en la base de
   pruebas: `odoo-bin -c /ruta/odoo.conf -d BASE_PRUEBAS -i
   alvina_website_order_entry --stop-after-init`. Para actualizar un addon ya
   instalado, usar `-u alvina_website_order_entry` en vez de `-i`.
4. Arrancar la instancia de pruebas por su procedimiento habitual y verificar la
   matriz completa. Revisar los assets del frontend, menús de ambos tamaños,
   color de marca y permisos de cada sucursal.
5. El despliegue real y cualquier reinicio requieren autorización expresa y el
   procedimiento de respaldo y actualización del administrador del servidor.

Los comandos anteriores son instrucciones: **no se ejecutaron en ALVIÑA**.
No requiere secretos nuevos para las pruebas unitarias. No compartir claves ni
contraseñas en el repositorio o en el chat.

Licencia del addon y código de este repositorio: AGPL-3.0-or-later.
