import os
import json
import threading
from urllib.parse import quote_plus
from decimal import Decimal

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse, Http404, HttpResponse
from django.views.decorators.http import require_http_methods, require_GET
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.db.models import Q, Sum, F, Count
from django.core import serializers
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

from .models import Plat, Commande, CommandeItem, TableRestaurant, Table, User
from .utils import download_plat_image


@require_GET
def plat_list(request):
    """
    API endpoint pour récupérer la liste des plats disponibles
    """
    plats = Plat.objects.filter(disponible=True).order_by('categorie', 'nom')
    data = serializers.serialize('json', plats, fields=('nom', 'description', 'prix', 'categorie', 'image'))
    return JsonResponse(data, safe=False)


def menu_view(request):
    """
    Affiche le menu des plats disponibles, organisés par catégorie
    """
    # Récupérer uniquement les plats disponibles
    plats_disponibles = Plat.objects.filter(disponible=True).order_by('categorie', 'nom')
    
    # Organiser les plats par catégorie
    categories = {}
    for plat in plats_disponibles:
        categorie_nom = plat.get_categorie_display()
        if categorie_nom not in categories:
            categories[categorie_nom] = []
        categories[categorie_nom].append(plat)
    
    context = {
        'categories': categories,
    }
    
    return render(request, 'menu/menu.html', context)

def download_images_for_plats(plats):
    """Fonction pour télécharger les images des plats en arrière-plan"""
    for plat in plats:
        if not plat.image:  # Ne télécharger que si l'image n'existe pas déjà
            try:
                download_plat_image(plat)
            except Exception as e:
                print(f"Erreur lors du téléchargement de l'image pour {plat.nom}: {str(e)}")

def menu_list(request):
    """
    Affiche la liste des plats disponibles avec leurs images
    """
    # Récupérer uniquement les plats disponibles
    plats_disponibles = Plat.objects.filter(disponible=True).order_by('categorie', 'nom')
    
    # Créer le répertoire des médias s'il n'existe pas
    os.makedirs(settings.MEDIA_ROOT / 'plats', exist_ok=True)
    
    # Mappage des noms de plats vers les noms de fichiers d'images
    plat_image_map = {
        'salade césar': 'salade-cesar.jpg',
        'tartare de saumon': 'tartare-saumon.jpg',
        'salade de poivrons': 'salade-de-poivrons-mixtes-vue-laterale.jpg',
        'salade de thon': 'salade-de-thon.jpg',
        'bœuf bourguignon': 'boeuf-bourguignon.jpg',
        'côtelettes d\'agneau': 'cotelettes-d-agneau-grillees.jpg',
        'poulet rôti': 'poulet-roti.jpg',
        'filet de bœuf': 'viande-grillee-de-filets-de-boeuf-aux-legumes.jpg',
        'poulet aux légumes': 'poulet-frit-aux-legumes-sur-une-table-en-bois.jpg',
        'nouilles au poulet': 'un-bol-de-nouilles-au-poulet-avec-legumes-et-sesame.jpg',
        'tarte tatin': 'tarte-tatin.jpg',
        'gâteau au chocolat': 'gros-plan-aerien-de-la-nourriture-cuite-du-moyen-orient-sur-une-plaque-blanche-avec-une-fourchette-et-un-couteau-de-cuisine.jpg',
        'eau minérale': 'eau.jpg',
        'jus de fruits frais': 'vin-rouge.jpg'
    }
    
    # Préparer les données des plats avec leurs images
    plats_avec_images = []
    for plat in plats_disponibles:
        # Vérifier si une image correspond au nom du plat
        image_nom = plat_image_map.get(plat.nom.lower(), None)
        image_url = f"/media/plats/{image_nom}" if image_nom and os.path.exists(settings.MEDIA_ROOT / 'plats' / image_nom) else None
        
        plats_avec_images.append({
            'plat': plat,
            'image_url': image_url
        })
    
    # Organiser les plats par catégorie
    categories = {}
    for plat_info in plats_avec_images:
        plat = plat_info['plat']
        categorie_nom = plat.get_categorie_display()
        if categorie_nom not in categories:
            categories[categorie_nom] = []
        categories[categorie_nom].append(plat_info)
    
    context = {
        'categories': categories,
    }
    
    return render(request, 'menu/menu_list.html', context)

@require_http_methods(["POST"])
@login_required
def commander_plat(request, plat_id):
    """
    API endpoint pour commander un plat
    """
    try:
        plat = get_object_or_404(Plat, id=plat_id, disponible=True)
        
        # Vérifier si l'utilisateur a déjà une commande en cours
        commande, created = Commande.objects.get_or_create(
            client=request.user,
            statut='en_attente',
            defaults={
                'table': None,  # À adapter selon votre logique de table
                'montant_total': Decimal('0.00')
            }
        )
        
        # Ajouter le plat à la commande
        commande_item, created = CommandeItem.objects.get_or_create(
            commande=commande,
            plat=plat,
            defaults={
                'quantite': 1,
                'prix_unitaire': plat.prix
            }
        )
        
        if not created:
            commande_item.quantite += 1
            commande_item.save()
        
        # Mettre à jour le montant total de la commande
        commande.montant_total = commande.items.aggregate(
            total=Sum(F('quantite') * F('prix_unitaire'))
        )['total'] or Decimal('0.00')
        commande.save()
        
        return JsonResponse({
            'success': True,
            'message': f"{plat.nom} a été ajouté à votre commande !",
            'commande_id': commande.id,
            'total_items': commande.items.count()
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f"Erreur lors de la commande : {str(e)}"
        }, status=400)
    # Cette vue n'est plus utilisée, on redirige vers la vue principale du menu
    return redirect('menu:menu')

@login_required
@require_http_methods(["POST"])
@csrf_exempt
@transaction.atomic
def creer_commande(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            items = data.get('items', [])
            
            if not items:
                return JsonResponse({'status': 'error', 'message': 'Le panier est vide'}, status=400)
            
            # Récupérer ou créer la table associée à l'utilisateur
            table, created = TableRestaurant.objects.get_or_create(
                utilisateur=request.user,
                defaults={'numero_table': f"Table-{request.user.id}"}
            )
            
            # Créer la commande
            commande = Commande.objects.create(
                table=table,
                statut='en_attente',
                montant_total=0
            )
            
            # Ajouter les articles à la commande
            total = 0
            for item in items:
                plat = get_object_or_404(Plat, id=item['id'], disponible=True)
                quantite = min(max(1, int(item.get('quantite', 1))), 10)  # Limiter à 10 max
                
                CommandeItem.objects.create(
                    commande=commande,
                    plat=plat,
                    quantite=quantite,
                    prix_unitaire=plat.prix
                )
                total += plat.prix * quantite
            
            # Mettre à jour le montant total
            commande.montant_total = total
            commande.save()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Commande créée avec succès',
                'commande_id': commande.id
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)

@login_required
def dashboard(request):
    """
    Affiche le tableau de bord avec les statistiques et les commandes récentes
    """
    # Récupérer les statistiques
    total_tables = Table.objects.count()
    tables_occupees = Table.objects.filter(statut='occupée').count()
    commandes_aujourdhui = Commande.objects.filter(
        date_commande__date=timezone.now().date()
    ).count()
    chiffre_affaires = Commande.objects.filter(
        statut='payée',
        date_commande__date=timezone.now().date()
    ).aggregate(total=Sum('montant_total'))['total'] or 0
    
    # Récupérer les commandes récentes
    commandes_recentes = Commande.objects.select_related('table').order_by('-date_commande')[:5]
    
    # Récupérer les plats populaires
    plats_populaires = Plat.objects.annotate(
        total_commandes=Count('commandeitem')
    ).order_by('-total_commandes')[:5]
    
    context = {
        'total_tables': total_tables,
        'tables_occupees': tables_occupees,
        'commandes_aujourdhui': commandes_aujourdhui,
        'chiffre_affaires': chiffre_affaires,
        'commandes_recentes': commandes_recentes,
        'plats_populaires': plats_populaires,
    }
    
    return render(request, 'menu/dashboard.html', context)

def login_view(request):
    """
    Gère la connexion des utilisateurs
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Identifiants invalides')
    
    return render(request, 'menu/login.html')

def logout_view(request):
    """
    Déconnecte l'utilisateur
    """
    logout(request)
    return redirect('login')
