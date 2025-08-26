## DOCUMENTATION

### Diagram

### models

````
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid

class Utilisateur(AbstractUser):
    ROLE_CHOICES = [
        ('client', 'Client'),
        ('vendeur', 'Vendeur'),
        ('admin', 'Administrateur'),
        ('gestionnaire', 'Gestionnaire de stock'),
    ]
    
    SEGMENT_CHOICES = [
        ('etudiant', 'Étudiant'),
        ('professionnel', 'Professionnel'),
        ('entreprise', 'Entreprise'),
        ('institution', 'Institution publique'),
    ]
    
    telephone = models.CharField(max_length=20, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='client')
    segment = models.CharField(max_length=20, choices=SEGMENT_CHOICES, blank=True)
    partenaire = models.ForeignKey('Partenaire', on_delete=models.SET_NULL, null=True, blank=True)
    email_verifie = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

class Partenaire(models.Model):
    nom = models.CharField(max_length=100)
    type_organisme = models.CharField(max_length=50, choices=[
        ('universite', 'Université'),
        ('ecole', 'École'),
        ('entreprise', 'Entreprise'),
        ('institution', 'Institution publique'),
    ])
    contact = models.CharField(max_length=100)
    email = models.EmailField()
    telephone = models.CharField(max_length=20)
    remise_speciale = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    def __str__(self):
        return self.nom

class Categorie(models.Model):
    nom = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True)
    ordre = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['ordre', 'nom']
    
    def __str__(self):
        return self.nom

class Marque(models.Model):
    nom = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='marques/', blank=True)
    
    def __str__(self):
        return self.nom

class Produit(models.Model):
    DISPONIBILITE_CHOICES = [
        ('en_stock', 'En stock'),
        ('rupture', 'Rupture de stock'),
        ('precommande', 'Précommande'),
    ]
    
    BADGE_CHOICES = [
        ('nouveau', 'Nouveau'),
        ('promo', 'Promotion'),
        ('populaire', 'Populaire'),
        ('etudiant', 'Remise étudiante'),
        ('pro', 'Remise professionnelle'),
    ]
    
    nom = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    description_courte = models.CharField(max_length=300)
    prix = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    prix_promo = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)])
    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE, related_name='produits')
    marque = models.ForeignKey(Marque, on_delete=models.CASCADE, related_name='produits')
    disponibilite = models.CharField(max_length=20, choices=DISPONIBILITE_CHOICES, default='en_stock')
    stock = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    badges = models.JSONField(default=list, blank=True)  # Liste de badges: ['nouveau', 'promo', etc.]
    specifications = models.JSONField(default=dict)  # {cpu: "Intel i7", ram: "16GB", etc.}
    images = models.JSONField(default=list)  # Liste URLs d'images
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    meta_titre = models.CharField(max_length=60, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)
    mots_cles = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-date_creation']
        indexes = [
            models.Index(fields=['nom', 'categorie']),
            models.Index(fields=['prix']),
            models.Index(fields=['disponibilite']),
        ]
    
    def __str__(self):
        return self.nom
    
    def get_prix_final(self, utilisateur=None):
        """Retourne le prix après application des remises"""
        prix = self.prix_promo if self.prix_promo else self.prix
        
        # Application des remises partenaires
        if utilisateur and utilisateur.partenaire and utilisateur.partenaire.remise_speciale:
            remise = utilisateur.partenaire.remise_speciale
            prix = prix * (1 - remise / 100)
        
        # Application des remises segment
        if utilisateur and utilisateur.segment == 'etudiant':
            prix = prix * 0.9  # 10% de remise étudiante
        
        return round(prix, 2)
    
    def est_en_stock(self):
        return self.disponibilite == 'en_stock' and self.stock > 0

class Adresse(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='adresses')
    nom_complet = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20)
    ligne1 = models.CharField(max_length=100)
    ligne2 = models.CharField(max_length=100, blank=True)
    ville = models.CharField(max_length=50)
    code_postal = models.CharField(max_length=10)
    pays = models.CharField(max_length=50, default='Sénégal')
    par_defaut = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Adresse"
        verbose_name_plural = "Adresses"
    
    def __str__(self):
        return f"{self.nom_complet} - {self.ville}"

class Panier(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Panier"
        verbose_name_plural = "Paniers"
    
    def __str__(self):
        if self.utilisateur:
            return f"Panier de {self.utilisateur.username}"
        return f"Panier session {self.session_key}"
    
    def get_total(self):
        return sum(item.get_sous_total() for item in self.items.all())
    
    def get_nombre_items(self):
        return sum(item.quantite for item in self.items.all())

class ItemPanier(models.Model):
    panier = models.ForeignKey(Panier, on_delete=models.CASCADE, related_name='items')
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    date_ajout = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Item panier"
        verbose_name_plural = "Items panier"
        unique_together = ['panier', 'produit']
    
    def __str__(self):
        return f"{self.quantite} x {self.produit.nom}"
    
    def get_sous_total(self):
        return self.produit.get_prix_final() * self.quantite

class Commande(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('confirmee', 'Confirmée'),
        ('en_preparation', 'En préparation'),
        ('expediee', 'Expédiée'),
        ('livree', 'Livrée'),
        ('annulee', 'Annulée'),
    ]
    
    MODE_PAIEMENT_CHOICES = [
        ('orange_money', 'Orange Money'),
        ('wave', 'Wave'),
        ('carte_credit', 'Carte de crédit'),
        ('virement', 'Virement bancaire'),
        ('especes', 'Paiement en espèces'),
    ]
    
    numero = models.CharField(max_length=20, unique=True, default=uuid.uuid4)
    client = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='commandes')
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    mode_paiement = models.CharField(max_length=20, choices=MODE_PAIEMENT_CHOICES)
    adresse_livraison = models.ForeignKey(Adresse, on_delete=models.PROTECT, related_name='commandes_livraison')
    adresse_facturation = models.ForeignKey(Adresse, on_delete=models.PROTECT, related_name='commandes_facturation')
    sous_total = models.DecimalField(max_digits=10, decimal_places=2)
    remise = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    frais_livraison = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    note = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-date_creation']
        verbose_name = "Commande"
        verbose_name_plural = "Commandes"
    
    def __str__(self):
        return f"Commande #{self.numero} - {self.client.username}"
    
    def save(self, *args, **kwargs):
        if not self.numero:
            # Générer un numéro de commande unique basé sur la date
            date_str = timezone.now().strftime('%Y%m%d')
            last_order = Commande.objects.filter(numero__startswith=date_str).order_by('numero').last()
            if last_order:
                last_num = int(last_order.numero[-4:])
                new_num = last_num + 1
            else:
                new_num = 1
            self.numero = f"{date_str}{new_num:04d}"
        
        super().save(*args, **kwargs)

class LigneCommande(models.Model):
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE, related_name='lignes')
    produit = models.ForeignKey(Produit, on_delete=models.PROTECT)
    quantite = models.PositiveIntegerField()
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)
    sous_total = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name = "Ligne de commande"
        verbose_name_plural = "Lignes de commande"
    
    def __str__(self):
        return f"{self.quantite} x {self.produit.nom} (Commande #{self.commande.numero})"

class Avis(models.Model):
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE, related_name='avis')
    auteur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    note = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    commentaire = models.TextField()
    date_creation = models.DateTimeField(auto_now_add=True)
    approuve = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Avis"
        verbose_name_plural = "Avis"
        unique_together = ['produit', 'auteur']
    
    def __str__(self):
        return f"Avis de {self.auteur.username} sur {self.produit.nom}"

class Promotion(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    type_promotion = models.CharField(max_length=20, choices=[
        ('pourcentage', 'Pourcentage'),
        ('montant_fixe', 'Montant fixe'),
        ('livraison_gratuite', 'Livraison gratuite'),
    ])
    valeur = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    produits = models.ManyToManyField(Produit, blank=True)
    categories = models.ManyToManyField(Categorie, blank=True)
    date_debut = models.DateTimeField()
    date_fin = models.DateTimeField()
    actif = models.BooleanField(default=True)
    segments_cibles = models.JSONField(default=list, blank=True)  # ['etudiant', 'professionnel', etc.]
    
    class Meta:
        ordering = ['-date_debut']
    
    def __str__(self):
        return self.nom
    
    def est_active(self):
        maintenant = timezone.now()
        return self.actif and self.date_debut <= maintenant <= self.date_fin

````
### SERVICES

````
from django.core.mail import send_mail

def envoyer_email_verification(utilisateur, token):
    sujet = "Vérification de votre adresse email"
    message = f"Bonjour {utilisateur.username},\n\nVeuillez vérifier votre adresse email en cliquant sur le lien suivant:\nhttp://example.com/verify-email/{token}/\n\nMerci!"
    send_mail(sujet, message, '
    
    
    
    
````
### ROLE ET PERMISSION

````
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission
from votre_app.models import Role
from django.contrib.contenttypes.models import ContentType

class Command(BaseCommand):
    help = 'Crée les rôles par défaut et leurs permissions'

    def handle(self, *args, **options):
        # Rôle Administrateur
        admin_role, created = Role.objects.get_or_create(
            nom='ADMINISTRATEUR',
            defaults={'description': 'Accès complet à toutes les fonctionnalités'}
        )
        
        # Rôle Gestionnaire
        gestionnaire_role, created = Role.objects.get_or_create(
            nom='GESTIONNAIRE',
            defaults={'description': 'Gestion des produits et commandes'}
        )
        
        # Rôle Vendeur
        vendeur_role, created = Role.objects.get_or_create(
            nom='VENDEUR',
            defaults={'description': 'Gestion des ventes et clients'}
        )
        
        # Rôle Client
        client_role, created = Role.objects.get_or_create(
            nom='CLIENT',
            defaults={'description': 'Utilisateur standard du site e-commerce'}
        )
        
        # Attribuer toutes les permissions à l'administrateur
        admin_role.permissions.set(Permission.objects.all())
        
        # Attribuer des permissions spécifiques au gestionnaire
        gestionnaire_permissions = Permission.objects.filter(
            codename__in=[
                'can_manage_products', 
                'can_manage_orders',
                'can_view_reports'
            ]
        )
        gestionnaire_role.permissions.set(gestionnaire_permissions)
        
        # Attribuer des permissions spécifiques au vendeur
        vendeur_permissions = Permission.objects.filter(
            codename__in=[
                'can_view_dashboard',
                'can_manage_orders'
            ]
        )
        vendeur_role.permissions.set(vendeur_permissions)
        
        self.stdout.write(
            self.style.SUCCESS('Rôles créés avec succès avec leurs permissions')
        )
````
### DECORATEUR ROLE ET PERMISSION 

````
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import user_passes_test

def role_requis(role_nom):
    """Décorateur pour restreindre l'accès aux utilisateurs avec un rôle spécifique"""
    def decorator(view_func):
        def wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return HttpResponseForbidden("Accès non autorisé")
            
            if request.user.role and request.user.role.nom == role_nom:
                return view_func(request, *args, **kwargs)
            
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            return HttpResponseForbidden("Accès non autorisé")
        return wrapped_view
    return decorator

def permissions_requises(permissions):
    """Décorateur pour restreindre l'accès aux utilisateurs avec des permissions spécifiques"""
    def decorator(view_func):
        def wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return HttpResponseForbidden("Accès non autorisé")
            
            # Vérifier chaque permission
            for perm in permissions:
                if not request.user.has_perm(perm):
                    return HttpResponseForbidden("Accès non autorisé")
            
            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator
````