from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Filtre personnalisé pour accéder à un élément d'un dictionnaire par clé dans un template.
    Utilisation : {{ dictionnaire|get_item:key }}
    """
    return dictionary.get(key, [])
