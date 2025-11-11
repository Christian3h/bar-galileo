from django import template
from django.contrib.humanize.templatetags.humanize import intcomma

register = template.Library()

@register.filter(name='format_price')
def format_price(value):
    """
    Filtro para formatear precios en formato colombiano (COP)
    Ejemplos:
    - 1000 -> $1.000
    - 50000 -> $50.000
    - 1250.50 -> $1.251 (redondea)
    """
    if value is None or value == '':
        return '$0'
    
    try:
        # Convertir a entero para eliminar los decimales (redondeando)
        price_int = int(round(float(value)))
        
        # Formatear con separador de miles usando intcomma
        formatted_price = intcomma(price_int)
        
        # Reemplazar la coma por un punto (formato colombiano)
        formatted_price = formatted_price.replace(',', '.')
        
        # Agregar el símbolo de peso colombiano
        return f'${formatted_price}'
    
    except (ValueError, TypeError):
        return '$0'

@register.filter(name='add_class')
def add_class(field, css_class):
    """
    Filtro para agregar clases CSS a campos de formulario
    Uso: {{ form.field|add_class:"mi-clase" }}
    """
    return field.as_widget(attrs={'class': css_class})
