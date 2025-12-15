from django import template

register = template.Library()

_MODULE_TRANSLATIONS = {
    "Backups": "Copias de seguridad",
    "Brands": "Marcas",
    "Categories": "Categorías",
    "Dashboard": "Panel",
    "Expenses": "Gastos",
    "Facturacion": "Facturación",
    "Nominas": "Nóminas",
    "Products": "Productos",
    "Providers": "Proveedores",
    "Reportes": "Reportes",
    "Reservations": "Reservas",
    "Roles": "Roles",
    "Tables": "Mesas",
    "Users": "Usuarios",
}

@register.filter(name="translate_module")
def translate_module(value: str) -> str:
    """Translate known module names to Spanish for display.

    Falls back to original if not found.
    """
    if not isinstance(value, str):
        return value
    return _MODULE_TRANSLATIONS.get(value.strip(), value)
