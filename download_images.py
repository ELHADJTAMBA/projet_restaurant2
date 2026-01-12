import os
import requests
from pathlib import Path

# Créer le dossier media/plats s'il n'existe pas
base_dir = Path(__file__).resolve().parent.parent
media_dir = base_dir / 'media' / 'plats'
media_dir.mkdir(parents=True, exist_ok=True)

# Nouveaux liens d'images plus fiables
plats = {
    'salade-cesar': 'https://img.freepik.com/photos-gratuite/deliciouse-salade-cesar-assiette_23-2148763757.jpg',
    'tartare-saumon': 'https://img.freepik.com/photos-gratuite/tartare-saumon-frais-herbes_2829-20044.jpg',
    'boeuf-bourguignon': 'https://img.freepik.com/photos-gratuite/boeuf-bourguignon-traditionnel-sauce-aux-champignons_2829-18855.jpg',
    'poulet-roti': 'https://img.freepik.com/photos-gratuite/cuisinier-tenant-assiette-poulet-roti-legumes_23-2148982425.jpg',
    'fondant-chocolat': 'https://img.freepik.com/photos-gratuite/fondant-chocolat-framboises_1147-2207.jpg',
    'tarte-tatin': 'https://img.freepik.com/photos-gratuite/tarte-tatin-pommes-caramelisees_23-2148764603.jpg',
    'eau': 'https://img.freepik.com/photos-gratuite/verre-eau-fraiche-gouttes-eau_23-2148253516.jpg',
    'vin-rouge': 'https://img.freepik.com/photos-gratuite/verre-vin-rouge-fond-noir_123827-29650.jpg'
}

# Télécharger chaque image
for nom_fichier, url in plats.items():
    chemin_image = media_dir / f'{nom_fichier}.jpg'
    if not chemin_image.exists():
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, stream=True, timeout=10)
            response.raise_for_status()
            
            with open(chemin_image, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f'✅ Image téléchargée : {chemin_image}')
        except Exception as e:
            print(f'❌ Erreur avec {url}: {str(e)}')
    else:
        print(f'✅ Image existe déjà : {chemin_image}')

print('✅ Téléchargement terminé !')
