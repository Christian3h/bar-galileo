from django import template
from django.http import QueryDict

register = template.Library()


@register.simple_tag
def url_replace(request, **kwargs):
    """
    Genera una URL manteniendo los parámetros GET actuales,
    excepto los que se pasan como argumentos.

    Uso en template:
    {% url_replace request page=2 %}
    """
    query = request.GET.copy()

    for key, value in kwargs.items():
        if value is not None:
            query[key] = value
        elif key in query:
            del query[key]

    return query.urlencode()
