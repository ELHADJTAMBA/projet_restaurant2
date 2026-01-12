from django.contrib import admin
from .models import TableRestaurant

@admin.register(TableRestaurant)
class TableRestaurantAdmin(admin.ModelAdmin):
    list_display = ('numero_table', 'nombre_places', 'etat', 'utilisateur')
    list_filter = ('etat',)
