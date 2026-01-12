from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    # URL de connexion
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    
    # URL de déconnexion
    path('logout/', auth_views.LogoutView.as_view(next_page='menu:menu'), name='logout'),
    
    # URL d'inscription
    path('register/', views.register, name='register'),
]
