# ALVIÑA — Portal de pedidos

Addon complementario **`alvina_website_order_entry`**. Se coloca junto a los
addons existentes; **no sustituye `alvinha_mrp`** ni requiere copiar todo el ZIP
original a este repositorio.

## Qué hace

- Añade «Realizar Pedido» a `/portal/production/new` como primer elemento del
  menú estándar, antes de «Contáctanos», tanto para visitantes como para usuarios.
- Mantiene `auth="user"` de las rutas originales; utiliza el login de Odoo.
- Selecciona mañana y establece ese mismo mínimo, calculado en **America/Lima**.
- Rechaza fechas ausentes, imposibles, actuales o pasadas **antes de ejecutar la
  creación original**, incluso si se manipula el HTML o el JSON-RPC.
- Comprueba explícitamente el CSRF que el JS original ya envía. Devuelve los
  errores en el formato que ese JS muestra, conservando selecciones y cantidades.
- Delega la creación válida al controlador original, sin añadir modelos, campos,
  permisos, `sudo()` ni modificaciones globales de fechas históricas.

Granate `#681412`, tomado del encabezado del formulario suministrado. Fuente
heredada del sitio; color ajustable con la variable CSS `--alvina-order-color`.
No hace falta instalar recursos JS nuevos.

## Dependencias identificadas en el ZIP

- Versión objetivo: Odoo **19.0**. El código suministrado usa rutas `jsonrpc` y
  contiene módulos con versiones 19.0; la versión del servidor aún debe confirmarse.
- Dependencias directas: **`website` y `alvinha_mrp`**.
- `alvinha_mrp` depende a su vez de `alvinha_base`, `mrp` y `website`, según su
  manifest original. Esos módulos deben seguir instalados y disponibles.
- Controlador real: `alvinha_mrp.controllers.main.PortalProductionController`.
- Plantilla real: `alvinha_mrp.production_form`.
- Campo del formulario: `date_order`; recepción: `/portal/production/create`.
- El flujo original crea/agrupa `mrp.production` mediante `date_start`, crea
  `mrp.production.contact.line` y genera `sale.order` con `commitment_date`.

El ZIP original no se redistribuye ni se modifica en este repositorio. El addon
complementario depende del código que ya mantiene el partner.

## Instalación por el partner

1. En una **base de pruebas**, confirmar Odoo 19 y la presencia de `alvinha_mrp`.
2. Copiar únicamente la carpeta **`alvina_website_order_entry`** a la raíz de
   addons del repositorio del partner, al mismo nivel que `alvinha_mrp`:

   ```text
   repositorio-del-partner/
   ├── alvinha_base/
   ├── alvinha_mrp/
   └── alvina_website_order_entry/    ← carpeta nueva completa
   ```

3. El partner incorpora el cambio y actualiza el código del servidor siguiendo
   su procedimiento habitual. La ruta debe estar incluida en `addons_path`.
4. En Odoo, actualizar la lista de aplicaciones y buscar el nombre técnico
   `alvina_website_order_entry` o «ALVIÑA - Acceso a pedidos». **Quitar el filtro
   predeterminado “Aplicaciones”**, porque es un módulo complementario
   (`application=False`). Instalarlo; si ya estaba instalado, actualizarlo.
5. Probar todos los casos de [docs/VALIDATION.md](docs/VALIDATION.md), incluyendo
   la creación real de un pedido en pruebas, antes de autorizar producción.

Alternativa de consola, usando el ejecutable/configuración reales del partner:

```bash
odoo-bin -c /ruta/odoo.conf -d BASE_PRUEBAS -i alvina_website_order_entry --stop-after-init
# Si ya estaba instalado: usar -u en lugar de -i.
```

Reiniciar por sí solo no instala el módulo ni actualiza las vistas. No se ha
reiniciado ningún servicio ni ejecutado estos comandos contra ALVIÑA.

## Validación ejecutada

Desde la raíz del repositorio:

```bash
python -m unittest discover -s tests -v
```

**20 pruebas locales aprobadas**. Cubren fechas, cambio de día Lima, CSRF,
rechazo previo a la delegación, conservación de parámetros y contrato de vistas.
Los tests del controlador usan dobles de Odoo y del padre: no demuestran que
Odoo se haya instalado ni que sus rutas HTTP/ORM funcionen en el servidor.

Se contrastaron los XPath del encabezado con Odoo 19 oficial y el de fecha con
el XML real del ZIP. No hay Odoo/PostgreSQL ni base de pruebas en este entorno.
**La instalación y el flujo completo deben validarse en staging antes de
producción. No se garantiza ausencia de fallos en un servidor no probado.**

## Alcance y revisión técnica

Consultar [docs/INTEGRATION.md](docs/INTEGRATION.md) para el detalle del código
original, compatibilidad y limitaciones. Un tema con encabezado propio puede
requerir adaptar la herencia. El enlace es el primer elemento del menú estándar,
no necesariamente el inmediatamente anterior a Contacto. Se suprimen duplicados
con la ruta interna; enlaces absolutos o botones propios del tema se revisan en
staging. El alcance es todos los sitios que usan esas plantillas estándar.

Licencia del addon complementario: AGPL-3.0-or-later.
