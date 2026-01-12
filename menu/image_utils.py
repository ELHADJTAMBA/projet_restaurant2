import os
import requests
from urllib.parse import quote_plus
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

def download_plat_image(plat):
    """
    Télécharge une image correspondant au plat depuis Unsplash
    et l'associe au plat.
    """
    try:
        print(f"Tentative de téléchargement d'image pour: {plat.nom}")
        
        # Vérifier si le plat a déjà une image
        if plat.image:
            print(f"Le plat {plat.nom} a déjà une image: {plat.image}")
            return False
            
        # Préparer la requête de recherche
        search_query = quote_plus(f"{plat.nom} {plat.categorie} food")
        url = f"https://source.unsplash.com/800x600/?{search_query}"
        print(f"URL de recherche d'image: {url}")
        
        # Télécharger l'image avec un timeout
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()
        
        # Vérifier que c'est bien une image
        content_type = response.headers.get('content-type', '').lower()
        print(f"Type de contenu reçu: {content_type}")
        
        if 'image' not in content_type:
            print(f"Le contenu n'est pas une image pour {plat.nom}")
            return False
            
        # Déterminer l'extension du fichier
        ext = 'jpg'  # Par défaut
        if 'jpeg' in content_type:
            ext = 'jpg'
        elif 'png' in content_type:
            ext = 'png'
            
        # Créer le dossier s'il n'existe pas
        os.makedirs('media/plats', exist_ok=True)
        
        # Générer un nom de fichier unique
        filename = f"plats/{plat.nom.lower().replace(' ', '_')}_{plat.id}.{ext}"
        filepath = os.path.join('media', filename)
        print(f"Enregistrement de l'image dans: {filepath}")
        
        # Sauvegarder l'image
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        # Mettre à jour le champ image du plat
        plat.image = filename
        plat.save()
        print(f"Image enregistrée avec succès pour {plat.nom}")
        return True
        
    except Exception as e:
        import traceback
        print(f"ERREUR lors du téléchargement de l'image pour {plat.nom}:")
        print(traceback.format_exc())
        return False
