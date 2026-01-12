from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponseRedirect
from django.urls import reverse

class RestaurantAdminSite(AdminSite):
    site_title = _("RestauPro - Administration")
    site_header = _("RestauPro - Tableau de bord")
    index_title = _("Gestion du restaurant")
    site_url = '/admin/'
    
    # Utilisation de notre template personnalisé
    index_template = 'admin/admin_dashboard.html'
    app_index_template = 'admin/app_index.html'
    login_template = 'admin/login.html'
    logout_template = 'admin/logout.html'
    
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        
        # Ajouter des URLs personnalisées ici si nécessaire
        custom_urls = [
            # Exemple d'URL personnalisée
            # path('custom-view/', self.admin_view(self.custom_view), name='custom-view'),
        ]
        
        return custom_urls + urls
    
    def get_app_list(self, request, app_label=None):
        """
        Retourne une liste triée des applications et des modèles.
        """
        app_dict = self._build_app_dict(request)
        
        # Trier les applications
        app_list = sorted(app_dict.values(), key=lambda x: x['name'].lower())
        
        # Trier les modèles dans chaque application
        for app in app_list:
            app['models'].sort(key=lambda x: x['name'].lower())
            
        return app_list
    
    def index(self, request, extra_context=None):
        """
        Surcharge de la vue d'index pour ajouter des données au contexte.
        """
        extra_context = extra_context or {}
        
        # Statistiques pour le tableau de bord
        from django.contrib.auth import get_user_model
        from django.db.models import Count, Sum, Q
        from django.utils import timezone
        from datetime import timedelta
        
        User = get_user_model()
        
        # Exemple de statistiques (à adapter selon vos modèles)
        try:
            # Nombre total d'utilisateurs
            total_users = User.objects.count()
            
            # Nombre d'utilisateurs actifs ce mois-ci
            last_month = timezone.now() - timedelta(days=30)
            new_users = User.objects.filter(date_joined__gte=last_month).count()
            
            # Vous pouvez ajouter d'autres statistiques ici en fonction de vos modèles
            # Par exemple : commandes, produits, etc.
            
            extra_context.update({
                'total_users': total_users,
                'new_users': new_users,
                # Ajoutez d'autres statistiques ici
            })
        except Exception as e:
            # En cas d'erreur (par exemple si les modèles ne sont pas encore migrés)
            print(f"Erreur lors du chargement des statistiques : {e}")
        
        return super().index(request, extra_context)
    
    def login(self, request, extra_context=None):
        """
        Redirige vers la page d'administration après la connexion.
        """
        if request.method == 'GET' and self.has_permission(request):
            # Déjà connecté, rediriger vers l'index de l'admin
            index_path = reverse('admin:index', current_app=self.name)
            return HttpResponseRedirect(index_path)
        
        # Sinon, afficher le formulaire de connexion normal
        return super().login(request, extra_context)

# Instance personnalisée de AdminSite
admin_site = RestaurantAdminSite(name='admin')
