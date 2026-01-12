from django.contrib import admin
from .models import Plat, Commande, CommandeItem, TableRestaurant

@admin.register(Plat)
class PlatAdmin(admin.ModelAdmin):
    list_display = ('nom', 'categorie', 'prix', 'disponible')
    list_filter = ('categorie', 'disponible')
    search_fields = ('nom', 'description')
    list_editable = ('disponible',)

class CommandeItemInline(admin.TabularInline):
    model = CommandeItem
    extra = 0
    readonly_fields = ('plat', 'quantite', 'prix_unitaire')
    can_delete = False

@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = ('id', 'table', 'date_commande', 'montant_total', 'statut')
    list_filter = ('statut', 'date_commande')
    search_fields = ('table__numero_table',)
    inlines = [CommandeItemInline]
    readonly_fields = ('date_commande', 'montant_total')

@admin.register(TableRestaurant)
class TableRestaurantAdmin(admin.ModelAdmin):
    list_display = ('numero_table', 'utilisateur', 'nombre_places')
    search_fields = ('numero_table', 'utilisateur__username')
