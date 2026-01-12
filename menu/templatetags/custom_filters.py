from django import template

register = template.Library()

@register.filter
def get_image_by_index(value, arg):
    """
    Retourne un élément d'une liste en fonction de l'index fourni.
    Si l'index est hors limites, retourne le premier élément.
    """
    try:
        index = int(arg) % len(value)
        return value[index]
    except (ValueError, IndexError, TypeError):
        return value[0] if value else ""
