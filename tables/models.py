from django.db import models
from accounts.models import User

class TableRestaurant(models.Model):

    ETAT_CHOICES = [
        ('libre', 'Libre'),
        ('attente', 'Commande en attente'),
        ('servie', 'Commande servie'),
        ('payee', 'Commande payée'),
    ]

    numero_table = models.CharField(max_length=10, unique=True)
    nombre_places = models.PositiveIntegerField()
    etat = models.CharField(
        max_length=10,
        choices=ETAT_CHOICES,
        default='libre'
    )

    utilisateur = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'Rtable'}
    )

    def __str__(self):
        return f"Table {self.numero_table}"
