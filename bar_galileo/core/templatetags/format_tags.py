from django import template
from django.contrib.humanize.templatetags.humanize import intcomma

register = template.Library()

@register.filter(name='format_price')
def format_price(value):
    if value is None:
        return ''
    
    # Convertir a entero para eliminar los decimales
    price_int = int(value)
    
    # Formatear con separador de miles
    formatted_price = intcomma(price_int)
    
    # Reemplazar la coma por un punto
    return formatted_price.replace(',', '.')
