from django import template
from decimal import Decimal

register = template.Library()

@register.filter(name='format_prix')
def format_prix(value):
    """
    Convertit un prix en franc guinéen (GNF) et le formate avec des séparateurs de milliers
    """
    try:
        # Conversion en décimal pour éviter les erreurs
        prix = Decimal(str(value))
        # Conversion en GNF (1 EUR ≈ 9,000 GNF, ajustez selon le taux actuel)
        prix_gnf = prix * 9000
        # Formatage avec séparateurs de milliers et ajout de 'GNF'
        return f"{prix_gnf:,.0f} GNF".replace(',', ' ')
    except (ValueError, TypeError):
        return f"{value} €"  # Fallback en cas d'erreur
