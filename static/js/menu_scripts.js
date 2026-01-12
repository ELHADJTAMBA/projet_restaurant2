// Fonction pour afficher des notifications
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    // Supprimer la notification après 5 secondes
    setTimeout(() => {
        notification.style.animation = 'fadeOut 0.3s ease-out';
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}

// Fonction pour gérer la commande
function commanderPlat(platId, platNom, event) {
    if (!platId || platId === '0') {
        console.error('ID de plat invalide');
        showNotification('Erreur : Impossible de commander ce plat (ID invalide)', 'error');
        return;
    }

    // Vérification de l'authentification
    const isAuthenticated = document.body.getAttribute('data-is-authenticated') === 'true';
    
    if (!isAuthenticated) {
        if (confirm('Vous devez être connecté pour commander. Voulez-vous vous connecter maintenant ?')) {
            window.location.href = '/accounts/login/?next=' + encodeURIComponent(window.location.pathname);
        }
        return;
    }

    // Afficher un indicateur de chargement
    const button = event && event.target ? event.target : null;
    let originalText = '';
    
    if (button) {
        originalText = button.textContent || '';
        button.disabled = true;
        button.textContent = 'Traitement...';
    }
    
    console.log(`Commande du plat: ${platNom} (ID: ${platId})`);
    
    // Récupérer le jeton CSRF depuis les cookies
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    const csrftoken = getCookie('csrftoken');
    
    // Exemple d'ajout au panier (à adapter selon votre logique)
    fetch(`/api/commander/${platId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
            'X-Requested-With': 'XMLHttpRequest'
        },
        credentials: 'same-origin'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Erreur réseau');
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            // Mettre à jour le compteur du panier s'il existe
            const cartCount = document.getElementById('cart-count');
            if (cartCount) {
                const currentCount = parseInt(cartCount.textContent) || 0;
                cartCount.textContent = currentCount + 1;
                cartCount.classList.add('animate-bounce');
                setTimeout(() => cartCount.classList.remove('animate-bounce'), 1000);
            }
            
            // Afficher une notification
            showNotification(`${platNom} a été ajouté à votre commande !`, 'success');
        } else {
            throw new Error(data.message || 'Erreur inconnue');
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
        showNotification(error.message || 'Erreur lors de la commande. Veuillez réessayer.', 'error');
    })
    .finally(() => {
        if (button) {
            button.disabled = false;
            button.textContent = originalText;
        }
    });
}

// Gestionnaire d'événements pour les boutons de commande
document.addEventListener('DOMContentLoaded', function() {
    console.log('Page de menu chargée avec succès !');
    
    // Ajouter les gestionnaires d'événements aux boutons de commande
    document.querySelectorAll('.menu-item-button').forEach(button => {
        button.addEventListener('click', function(event) {
            const platId = this.getAttribute('data-plat-id');
            const platNom = this.getAttribute('data-plat-nom');
            commanderPlat(platId, platNom, event);
        });
    });
});
