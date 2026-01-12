import os
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.core.files.storage import default_storage

User = get_user_model()

def plat_image_path(instance, filename):
    # Génère un nom de fichier unique pour chaque image
    ext = filename.split('.')[-1]
    filename = f"{instance.nom.lower().replace(' ', '_')}_{instance.id}.{ext}"
    return os.path.join('plats', filename)

class Table(models.Model):
    STATUT_CHOICES = [
        ('libre', 'Libre'),
        ('occupée', 'Occupée'),
        ('réservée', 'Réservée'),
        ('hors_service', 'Hors service'),
    ]
    
    numero = models.CharField(max_length=10, unique=True)
    capacite = models.PositiveIntegerField(default=4)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='libre')
    emplacement = models.CharField(max_length=100, blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Table'
        verbose_name_plural = 'Tables'
        ordering = ['numero']
    
    def __str__(self):
        return f"Table {self.numero} - {self.get_statut_display()}"

class TableRestaurant(models.Model):
    numero_table = models.CharField(max_length=50, unique=True)
    nombre_places = models.PositiveIntegerField(default=4)
    utilisateur = models.OneToOneField(User, on_delete=models.CASCADE, related_name='table')
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Table {self.numero_table}"

class Plat(models.Model):
    CATEGORIES = [
        ('ENTREE', 'Entrée'),
        ('PLAT', 'Plat'),
        ('DESSERT', 'Dessert'),
        ('BOISSON', 'Boisson'),
    ]

    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    prix = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    categorie = models.CharField(max_length=10, choices=CATEGORIES)
    disponible = models.BooleanField(default=True)
    image = models.ImageField(upload_to=plat_image_path, blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['categorie', 'nom']
        verbose_name = 'Plat'
        verbose_name_plural = 'Plats'

    def __str__(self):
        return f"{self.nom} - {self.prix}€"

    def save(self, *args, **kwargs):
        # Supprimer l'ancienne image si elle existe et est différente
        if self.pk:
            try:
                old_plat = Plat.objects.get(pk=self.pk)
                if old_plat.image and old_plat.image != self.image:
                    if default_storage.exists(old_plat.image.name):
                        default_storage.delete(old_plat.image.name)
            except Plat.DoesNotExist:
                pass

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Supprimer le fichier image lors de la suppression du plat
        if self.image:
            if default_storage.exists(self.image.name):
                default_storage.delete(self.image.name)
        super().delete(*args, **kwargs)

class Commande(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('en_preparation', 'En préparation'),
        ('prete', 'Prête à servir'),
        ('servie', 'Servie'),
        ('payee', 'Payée'),
        ('annulee', 'Annulée'),
    ]

    table = models.ForeignKey(Table, on_delete=models.PROTECT, related_name='commandes')
    table_restaurant = models.ForeignKey(TableRestaurant, on_delete=models.PROTECT, related_name='commandes', null=True, blank=True)
    date_commande = models.DateTimeField(auto_now_add=True)
    montant_total = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    serveur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='commandes_serveur')

    def __str__(self):
        return f"Commande #{self.id} - Table {self.table.numero_table}"

class CommandeItem(models.Model):
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE, related_name='items')
    plat = models.ForeignKey(Plat, on_delete=models.PROTECT)
    quantite = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    prix_unitaire = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(0)])

    def __str__(self):
        return f"{self.quantite}x {self.plat.nom} (Commande #{self.commande.id})"

    @property
    def total(self):
        return self.quantite * self.prix_unitaire
