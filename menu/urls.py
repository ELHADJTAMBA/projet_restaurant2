from django.urls import path
from . import views

app_name = 'menu'

urlpatterns = [
    path('', views.menu_list, name='menu_list'),   # /menu/
    path('api/plats/', views.plat_list, name='plat_list'),
    path('api/commander/<int:plat_id>/', views.commander_plat, name='commander_plat'),
    path('dashboard/', views.dashboard, name='dashboard'),
]
