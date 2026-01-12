from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('login', 'role', 'actif', 'date_creation')
    list_filter = ('role', 'actif')
