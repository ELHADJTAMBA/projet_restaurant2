from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.urls import reverse_lazy

# Utilisation de notre AdminSite personnalisé
from .admin_site import admin_site

urlpatterns = [
    # Redirection de la racine vers l'admin
    path('', RedirectView.as_view(url=reverse_lazy('admin:index'), permanent=False)),
    
    # Interface d'administration personnalisée
    path('admin/', admin_site.urls),
    
    # URLs des applications
    path('accounts/', include('accounts.urls')),
    path('tables/', include('tables.urls')),
    path('menu/', include('menu.urls')),
]

# Configuration pour servir les fichiers statiques et médias en développement
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # Debug toolbar
    try:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
    except ImportError:
        pass
