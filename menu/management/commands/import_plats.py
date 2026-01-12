import os
import requests
from django.core.management.base import BaseCommand
from django.core.files import File
from menu.models import Plat
from pathlib import Path
from django.conf import settings

class Command(BaseCommand):
    help = 'Importe les plats dans la base de données'

    def handle(self, *args, **options):
        # Catégories et leurs plats
        categories = {
            'ENTRÉES': [
                'Salade verte',
                'Salade César',
                'Salade de tomates et oignons',
                'Soupe du jour',
                'Potage de légumes',
                'Beignets de crevettes',
                'Accras de morue',
                'Pastels (viande / poisson)',
                'Nem au poulet',
                'Bruschetta'
            ],
            'PLATS - VIANDE': [
                'Poulet braisé',
                'Poulet rôti',
                'Poulet yassa',
                'Bœuf sauté aux légumes',
                'Steak grillé',
                'Brochettes de viande',
                'Côtelette d\'agneau',
                'Hamburger classique',
                'Cheeseburger'
            ],
            'PLATS - POISSON': [
                'Poisson braisé',
                'Poisson frit',
                'Poisson sauce tomate',
                'Crevettes sautées',
                'Tilapia grillé',
                'Thiof (riz au poisson)',
                'Riz au poisson blanc'
            ],
            'PLATS TRADITIONNELS': [
                'Riz sauce arachide',
                'Riz sauce feuille',
                'Riz sauce tomate',
                'Riz gras',
                'Attiéké poisson',
                'Foutou banane',
                'Tô + sauce gombo',
                'Couscous africain'
            ],
            'PLATS MODERNES': [
                'Spaghetti bolognaise',
                'Spaghetti carbonara',
                'Lasagnes',
                'Pizza margherita',
                'Pizza poulet',
                'Sandwich au poulet',
                'Shawarma',
                'Tacos'
            ],
            'ACCOMPAGNEMENTS': [
                'Riz blanc',
                'Riz gras',
                'Frites',
                'Banane plantain frite',
                'Attiéké',
                'Légumes sautés',
                'Purée de pommes de terre'
            ],
            'DESSERTS': [
                'Gâteau au chocolat',
                'Gâteau à la vanille',
                'Crème caramel',
                'Flan',
                'Mousse au chocolat',
                'Salade de fruits',
                'Fruits frais',
                'Beignets sucrés',
                'Glace (vanille, chocolat, fraise)'
            ],
            'BOISSONS NON ALCOOLISÉES': [
                'Eau minérale',
                'Eau gazeuse',
                'Jus d\'orange',
                'Jus d\'ananas',
                'Jus de mangue',
                'Jus de bissap',
                'Jus de gingembre',
                'Coca-Cola',
                'Fanta',
                'Sprite',
                'Thé',
                'Café',
                'Lait'
            ],
            'BOISSONS ALCOOLISÉES': [
                'Bière',
                'Vin rouge',
                'Vin blanc',
                'Vin rosé',
                'Whisky',
                'Vodka',
                'Rhum',
                'Cocktail maison'
            ]
        }

        # Prix par défaut par catégorie
        prix_par_categorie = {
            'ENTRÉES': 5000,
            'PLATS - VIANDE': 12000,
            'PLATS - POISSON': 15000,
            'PLATS TRADITIONNELS': 10000,
            'PLATS MODERNES': 13000,
            'ACCOMPAGNEMENTS': 3000,
            'DESSERTS': 4000,
            'BOISSONS NON ALCOOLISÉES': 2000,
            'BOISSONS ALCOOLISÉES': 5000
        }

        # Créer les dossiers nécessaires
        media_dir = Path(settings.MEDIA_ROOT) / 'plats'
        media_dir.mkdir(parents=True, exist_ok=True)

        # Dictionnaire pour mapper les noms de plats aux noms de fichiers d'images
        images_plats = {
            # Entrées
            'Salade verte': 'salade-verte.jpg',
            'Salade César': 'salade-cesar.jpg',
            'Salade de tomates et oignons': 'salade-tomate-oignon.jpg',
            'Soupe du jour': 'soupe-jour.jpg',
            'Potage de légumes': 'potage-legumes.jpg',
            'Beignets de crevettes': 'beignets-crevettes.jpg',
            'Accras de morue': 'accras-morue.jpg',
            'Pastels (viande / poisson)': 'pastels.jpg',
            'Nem au poulet': 'nem-poulet.jpg',
            'Bruschetta': 'bruschetta.jpg',
            
            # Plats viande
            'Poulet braisé': 'poulet-braise.jpg',
            'Poulet rôti': 'poulet-roti.jpg',
            'Poulet yassa': 'poulet-yassa.jpg',
            'Bœuf sauté aux légumes': 'boeuf-legumes.jpg',
            'Steak grillé': 'steak-grille.jpg',
            'Brochettes de viande': 'brochettes-viande.jpg',
            'Côtelette d\'agneau': 'cotelette-agneau.jpg',
            'Hamburger classique': 'hamburger.jpg',
            'Cheeseburger': 'cheeseburger.jpg',
            
            # Plats poisson
            'Poisson braisé': 'poisson-braise.jpg',
            'Poisson frit': 'poisson-frit.jpg',
            'Poisson sauce tomate': 'poisson-sauce-tomate.jpg',
            'Crevettes sautées': 'crevettes-sautees.jpg',
            'Tilapia grillé': 'tilapia-grille.jpg',
            'Thiof (riz au poisson)': 'thiof.jpg',
            'Riz au poisson blanc': 'riz-poisson-blanc.jpg',
            
            # Plats traditionnels
            'Riz sauce arachide': 'riz-rachide.jpg',
            'Riz sauce feuille': 'riz-feuille.jpg',
            'Riz sauce tomate': 'riz-tomate.jpg',
            'Riz gras': 'riz-gras.jpg',
            'Attiéké poisson': 'attieke-poisson.jpg',
            'Foutou banane': 'foutou-banane.jpg',
            'Tô + sauce gombo': 'to-sauce-gombo.jpg',
            'Couscous africain': 'couscous-africain.jpg',
            
            # Plats modernes
            'Spaghetti bolognaise': 'spaghetti-bolo.jpg',
            'Spaghetti carbonara': 'spaghetti-carbonara.jpg',
            'Lasagnes': 'lasagnes.jpg',
            'Pizza margherita': 'pizza-margherita.jpg',
            'Pizza poulet': 'pizza-poulet.jpg',
            'Sandwich au poulet': 'sandwich-poulet.jpg',
            'Shawarma': 'shawarma.jpg',
            'Tacos': 'tacos.jpg',
            
            # Desserts
            'Gâteau au chocolat': 'gateau-chocolat.jpg',
            'Gâteau à la vanille': 'gateau-vanille.jpg',
            'Crème caramel': 'creme-caramel.jpg',
            'Flan': 'flan.jpg',
            'Mousse au chocolat': 'mousse-chocolat.jpg',
            'Salade de fruits': 'salade-fruits.jpg',
            'Fruits frais': 'fruits-frais.jpg',
            'Beignets sucrés': 'beignets-sucres.jpg',
            'Glace (vanille, chocolat, fraise)': 'glace.jpg',
            
            # Boissons
            'Eau minérale': 'eau.jpg',
            'Eau gazeuse': 'eau-gazeuse.jpg',
            'Jus d\'orange': 'jus-orange.jpg',
            'Jus d\'ananas': 'jus-ananas.jpg',
            'Jus de mangue': 'jus-mangue.jpg',
            'Jus de bissap': 'jus-bissap.jpg',
            'Jus de gingembre': 'jus-gingembre.jpg',
            'Coca-Cola': 'coca.jpg',
            'Fanta': 'fanta.jpg',
            'Sprite': 'sprite.jpg',
            'Thé': 'the.jpg',
            'Café': 'cafe.jpg',
            'Lait': 'lait.jpg',
            'Bière': 'biere.jpg',
            'Vin rouge': 'vin-rouge.jpg',
            'Vin blanc': 'vin-blanc.jpg',
            'Vin rosé': 'vin-rose.jpg',
            'Whisky': 'whisky.jpg',
            'Vodka': 'vodka.jpg',
            'Rhum': 'rhum.jpg',
            'Cocktail maison': 'cocktail.jpg'
        }

        # Télécharger les images manquantes
        base_url = 'https://raw.githubusercontent.com/chef-ai/food-images/main/'
        
        for nom_plat, image_name in images_plats.items():
            image_path = media_dir / image_name
            if not image_path.exists():
                try:
                    image_url = f"{base_url}{image_name}"
                    response = requests.get(image_url, stream=True)
                    response.raise_for_status()
                    with open(image_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    self.stdout.write(self.style.SUCCESS(f'✅ Téléchargé: {image_name}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'❌ Erreur pour {image_name}: {str(e)}'))

        # Ajouter les plats à la base de données
        for categorie, plats in categories.items():
            for nom_plat in plats:
                if not Plat.objects.filter(nom=nom_plat).exists():
                    plat = Plat(
                        nom=nom_plat,
                        description=f'Délicieux {nom_plat.lower()} préparé avec des ingrédients frais.',
                        prix=prix_par_categorie.get(categorie, 5000) / 100,  # Convertir en euros
                        categorie='PLAT',  # À adapter selon votre modèle
                        disponible=True
                    )
                    
                    # Associer l'image si elle existe
                    image_name = images_plats.get(nom_plat)
                    if image_name and (media_dir / image_name).exists():
                        with open(media_dir / image_name, 'rb') as f:
                            plat.image.save(image_name, File(f), save=False)
                    
                    plat.save()
                    self.stdout.write(self.style.SUCCESS(f'✅ Ajouté: {nom_plat}'))
                else:
                    self.stdout.write(self.style.WARNING(f'⚠️ Existe déjà: {nom_plat}'))

        self.stdout.write(self.style.SUCCESS('\n✅ Tous les plats ont été importés avec succès !'))
