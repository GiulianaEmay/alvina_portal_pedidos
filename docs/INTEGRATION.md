# Integración con el módulo real

## Fuentes inspeccionadas

Archivo facilitado: `alvinha-cybe (3).zip`.

| Componente | Identificación real |
| --- | --- |
| Addon | `alvinha_mrp` |
| Dependencias del original | `alvinha_base`, `mrp`, `website` |
| Controlador | `controllers/main.py`, clase `PortalProductionController` |
| Formulario | método `portal_production_form`, `/portal/production/new` |
| Receptor de creación | método `portal_create_production`, `/portal/production/create`, POST JSON-RPC |
| Plantilla | `views/portal_production_templates.xml`, `alvinha_mrp.production_form` |
| Input | `date_order`, tipo `date` |
| JS original | `static/src/js/public_widget.js`, `_collectFormData` / `_onSubmit` |
| Producción y asociaciones | `mrp.production.date_start`, `mrp.production.contact.line` |
| Venta | `sale.order.commitment_date` |

## Cambios implementados

El controlador hereda la clase identificada y vuelve a decorar sus dos métodos
con `auth='user'`. Conserva el tipo JSON-RPC, las rutas y el manejo original de
éxito/error mediante la herencia de rutas de Odoo.

En GET, llama al padre y cambia únicamente `response.qcontext['today']` antes
del renderizado lazy. La plantilla heredada modifica solo atributos del input:
`value`, `min`, `required` e `id`. Continúa siendo un calendario editable; no se
copia el formulario ni se tocan los selectores.

En creación, comprueba primero el token CSRF ya enviado por el JS original,
valida `date_order` en Lima y únicamente entonces delega al padre con todos los
parámetros existentes. El error se devuelve como `{'error': mensaje}`, formato
que el JS existente muestra sin recargar ni vaciar el formulario. Ningún pedido
con fecha rechazada llega a la creación original, incluida la creación múltiple.
Los formularios históricos no heredan la vista modificada y no se añaden
restricciones globales a los modelos.

El controlador original usa `self.env` en el formulario y notificaciones, aunque
`http.Controller` estándar expone el entorno mediante `request.env`. La extensión
incluye una propiedad de compatibilidad `env` que devuelve `request.env`, sin
cambiar el módulo original ni sus métodos de negocio.

## Comportamiento que se conserva

Se mantienen el cálculo y disponibilidad de agrupadores, el selector existente
de empresas/sucursales, cantidades, alertas de duplicados, asociación de contactos,
agrupación de producción y creación de ventas. La conversión de la fecha a rangos
UTC y el uso de cookie de zona horaria del **flujo original** no se modifican:
la nueva regla de default/mínimo y validación sí usa siempre Lima. Cambiar esa
conversión afectaría a la agrupación de pedidos y requiere una revisión separada.

## Limitaciones que requieren staging

- La versión instalada y el tema real no han podido verificarse. La consulta
  pública del sitio desde este entorno fue bloqueada por el proxy (403).
- Los menús personalizados que no llamen a `website.navbar_nav` no quedan
  cubiertos por la herencia. La deduplicación cubre rutas internas equivalentes,
  no enlaces absolutos ni botones externos a `website.submenu`. Un nodo de menú
  desplegable con esa URL se suprime con sus hijos; revisar la estructura real.
- No se han ejecutado login, renderizado Odoo, pedidos reales ni pruebas de ORM.
- La seguridad original usa `sudo()` y acepta `partner_id` del cliente sin una
  comprobación explícita de pertenencia en el receptor inspeccionado. El selector
  HTML `readonly` no sustituye esa comprobación. Esta extensión no amplía permisos,
  pero **no certifica las restricciones de sucursal del original**. El partner
  debe probar solicitudes manipuladas; si no existe otra capa de control en la
  instalación real, se necesita corregir esa validación antes de publicar.
- `/portal/get_partners` del addon `alvinha_base` está declarado `auth='public'`
  y usa `sudo()` en el código recibido. Su acceso se debe revisar con el partner;
  esta ampliación no cambia esa ruta.

No instalar todo el ZIP como sustitución de módulos sin revisar con el partner:
para esta entrega se añade únicamente `alvina_website_order_entry`.
