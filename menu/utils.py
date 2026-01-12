import os
import requests
from urllib.parse import quote_plus
from django.conf import settings
from django.core.files import File
from io import BytesIO

def download_plat_image(plat):
    """
    Télécharge une image pour un plat en fonction de son nom
    Retourne l'URL de l'image téléchargée ou None en cas d'échec
    """
    try:
        # Vérifier si le répertoire de destination existe
        plats_dir = os.path.join(settings.MEDIA_ROOT, 'plats')
        os.makedirs(plats_dir, exist_ok=True)
        
        # Créer un nom de fichier sécurisé
        safe_name = ''.join(c if c.isalnum() else '_' for c in plat.nom.lower())
        filename = f"plats/{safe_name}_{plat.id}.jpg"
        file_path = os.path.join(settings.MEDIA_ROOT, filename)
        
        # Vérifier si l'image existe déjà
        if os.path.exists(file_path):
            # Si le plat n'a pas encore d'image dans la base de données, la mettre à jour
            if not plat.image:
                with open(file_path, 'rb') as f:
                    plat.image.save(filename, File(f), save=True)
                return plat.image.url
            return f"{settings.MEDIA_URL}{filename}"
        
        # Télécharger une nouvelle image
        search_query = quote_plus(f"{plat.nom} food")
        url = f"https://source.unsplash.com/featured/800x600/?{search_query}"
        
        # Configuration de la requête avec timeout
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, stream=True, timeout=10)
        response.raise_for_status()
        
        # Vérifier que la réponse contient bien une image
        content_type = response.headers.get('content-type', '')
        if 'image' not in content_type:
            print(f"La réponse n'est pas une image valide pour {plat.nom}")
            return None
        
        # Sauvegarder l'image
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(8192):
                if chunk:
                    f.write(chunk)
        
        # Mettre à jour le champ image du plat
        with open(file_path, 'rb') as f:
            plat.image.save(filename, File(f), save=True)
        
        print(f"Image téléchargée avec succès pour {plat.nom}: {plat.image.url}")
        return plat.image.url
        
    except requests.exceptions.RequestException as e:
        print(f"Erreur de requête pour {plat.nom}: {str(e)}")
    except IOError as e:
        print(f"Erreur d'écriture du fichier pour {plat.nom}: {str(e)}")
    except Exception as e:
        print(f"Erreur inattendue pour {plat.nom}: {str(e)}")
    
    return None
