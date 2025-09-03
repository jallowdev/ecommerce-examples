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
        
        
        # Création d'un groupe avec des permissions spécifiques
groupe_administrateur, created = Group.objects.get_or_create(name='Administrateurs')

# Récupération des permissions pour une fonctionnalité
permission_ajout = Permission.objects.get(codename='add_article')
permission_modification = Permission.objects.get(codename='change_article')
permission_suppression = Permission.objects.get(codename='delete_article')

# Ajout des permissions au groupe
groupe_administrateur.permissions.add(permission_ajout, permission_modification, permission_suppression)
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

### MIDDLEWARE REDIRECTION DOMAINE

````
# middleware.py
import re
from django.http import Http404
from django.conf import settings
from .models import Tenant

class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        host = request.get_host()
        domain = host.split(':')[0]  # Remove port if present
        
        # Check for subdomain or full domain
        tenant = None
        if settings.DEBUG:
            # In development, use a header or default tenant
            tenant_domain = request.headers.get('X-Tenant-Domain', 'default.localhost')
            tenant = Tenant.objects.filter(domain=tenant_domain).first()
        else:
            # In production, match domain
            tenant = Tenant.objects.filter(domain=domain).first()
            
            if not tenant:
                # Check for subdomain pattern
                subdomain = domain.split('.')[0]
                if subdomain != 'www':
                    tenant = Tenant.objects.filter(domain__icontains=subdomain).first()
        
        if not tenant:
            raise Http404("Tenant not found")
            
        request.tenant = tenant
        response = self.get_response(request)
        return response
        
        
        

````
### Services de Gestion de Stock

````
# services/inventory_service.py
from django.db import transaction
from django.utils import timezone
from ..models import Inventory, InventoryHistory, Product

class InventoryService:
    @staticmethod
    @transaction.atomic
    def update_inventory(product, quantity_change, action, reason="", reference=""):
        """Mettre à jour le stock de manière transactionnelle"""
        inventory, created = Inventory.objects.get_or_create(
            product=product,
            defaults={'quantity': 0}
        )
        
        previous_quantity = inventory.quantity
        new_quantity = inventory.quantity + quantity_change
        
        if new_quantity < 0:
            raise ValueError("Stock insuffisant")
        
        inventory.quantity = new_quantity
        inventory.save()
        
        # Enregistrer l'historique
        InventoryHistory.objects.create(
            inventory=inventory,
            action=action,
            quantity=quantity_change,
            previous_quantity=previous_quantity,
            new_quantity=new_quantity,
            reason=reason,
            reference=reference
        )
        
        return inventory
    
    @staticmethod
    def get_low_stock_products(tenant):
        """Obtenir les produits en faible stock"""
        return Inventory.objects.filter(
            tenant=tenant,
            quantity__lte=models.F('low_stock_threshold')
        ).select_related('product')
    
    @staticmethod
    def get_inventory_history(tenant, product_id=None, start_date=None, end_date=None):
        """Obtenir l'historique des stocks"""
        queryset = InventoryHistory.objects.filter(tenant=tenant)
        
        if product_id:
            queryset = queryset.filter(inventory__product_id=product_id)
        
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)
        
        return queryset.order_by('-created_at')
        
        
# api_views.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.db import transaction
from .models import Inventory, InventoryHistory, Product
from .serializers import InventorySerializer, InventoryHistorySerializer
from .services.inventory_service import InventoryService

class InventoryAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = InventorySerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        return Inventory.objects.filter(tenant=self.request.tenant)
    
    @transaction.atomic
    def update(self, request, *args, **kwargs):
        inventory = self.get_object()
        quantity_change = request.data.get('quantity_change', 0)
        action = request.data.get('action', 'adjust')
        reason = request.data.get('reason', '')
        
        try:
            updated_inventory = InventoryService.update_inventory(
                inventory.product, quantity_change, action, reason
            )
            serializer = self.get_serializer(updated_inventory)
            return Response(serializer.data)
        except ValueError as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

class LowStockAlertAPIView(generics.ListAPIView):
    serializer_class = InventorySerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        return InventoryService.get_low_stock_products(self.request.tenant)

class InventoryHistoryAPIView(generics.ListAPIView):
    serializer_class = InventoryHistorySerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        product_id = self.request.query_params.get('product_id')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        return InventoryService.get_inventory_history(
            self.request.tenant, product_id, start_date, end_date
        )
````
### Services E-Commerce Complets

````
# services/cart_service.py
from django.db import transaction
from django.utils import timezone
from ..models import Cart, CartItem, Product, ProductVariant

class CartService:
    @staticmethod
    def get_or_create_cart(request):
        """Obtenir ou créer un panier pour l'utilisateur ou la session"""
        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(
                tenant=request.tenant,
                user=request.user
            )
        else:
            if not request.session.session_key:
                request.session.create()
            cart, created = Cart.objects.get_or_create(
                tenant=request.tenant,
                session_key=request.session.session_key,
                user=None
            )
        return cart
    
    @staticmethod
    @transaction.atomic
    def add_to_cart(cart, product_id, variant_id=None, quantity=1):
        """Ajouter un produit au panier"""
        try:
            product = Product.objects.get(id=product_id, tenant=cart.tenant)
            variant = None
            if variant_id:
                variant = ProductVariant.objects.get(id=variant_id, product=product)
            
            # Vérifier le stock
            if product.tracked:
                if variant:
                    if variant.inventory_quantity < quantity:
                        raise ValueError("Stock insuffisant pour cette variante")
                else:
                    if product.inventory.quantity < quantity:
                        raise ValueError("Stock insuffisant")
            
            # Ajouter ou mettre à jour l'article
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                variant=variant,
                defaults={'quantity': quantity}
            )
            
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
            
            return cart_item
        except (Product.DoesNotExist, ProductVariant.DoesNotExist):
            raise ValueError("Produit ou variante non trouvé")
    
    @staticmethod
    @transaction.atomic
    def update_cart_item(cart_item_id, quantity):
        """Mettre à jour la quantité d'un article"""
        cart_item = CartItem.objects.get(id=cart_item_id)
        
        if quantity <= 0:
            cart_item.delete()
            return None
        
        # Vérifier le stock
        if cart_item.product.tracked:
            available_stock = cart_item.variant.inventory_quantity if cart_item.variant else cart_item.product.inventory.quantity
            if available_stock < quantity:
                raise ValueError("Stock insuffisant")
        
        cart_item.quantity = quantity
        cart_item.save()
        return cart_item
    
    @staticmethod
    def get_cart_total(cart):
        """Calculer le total du panier"""
        return sum(item.total for item in cart.items.all())
        
    # services/order_service.py
from django.db import transaction
from django.utils import timezone
import uuid
from ..models import Order, OrderItem, Cart, CartItem, Inventory
from .inventory_service import InventoryService

class OrderService:
    @staticmethod
    @transaction.atomic
    def create_order_from_cart(cart, payment_method, billing_address, shipping_address):
        """Créer une commande à partir du panier"""
        if cart.items.count() == 0:
            raise ValueError("Le panier est vide")
        
        # Vérifier le stock avant création de commande
        for item in cart.items.all():
            if item.product.tracked:
                available_stock = item.variant.inventory_quantity if item.variant else item.product.inventory.quantity
                if available_stock < item.quantity:
                    raise ValueError(f"Stock insuffisant pour {item.product.name}")
        
        # Calculer les totaux
        subtotal = sum(item.total for item in cart.items.all())
        tax_amount = subtotal * 0.2  # Exemple: 20% TVA
        shipping_cost = 0  # À calculer selon la logique métier
        total = subtotal + tax_amount + shipping_cost
        
        # Créer la commande
        order = Order.objects.create(
            tenant=cart.tenant,
            order_number=str(uuid.uuid4())[:8].upper(),
            customer=cart.user if cart.user else None,
            payment_method=payment_method,
            billing_address=billing_address,
            shipping_address=shipping_address,
            subtotal=subtotal,
            tax_amount=tax_amount,
            shipping_cost=shipping_cost,
            total=total
        )
        
        # Créer les articles de commande
        for cart_item in cart.items.all():
            price = cart_item.variant.price if cart_item.variant else cart_item.product.base_price
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                variant=cart_item.variant,
                quantity=cart_item.quantity,
                price=price
            )
            
            # Mettre à jour le stock
            if cart_item.product.tracked:
                quantity_change = -cart_item.quantity
                InventoryService.update_inventory(
                    cart_item.product,
                    quantity_change,
                    'sold',
                    reason=f"Vente commande {order.order_number}",
                    reference=order.order_number
                )
        
        # Vider le panier
        cart.items.all().delete()
        
        return order
    
    @staticmethod
    @transaction.atomic
    def process_payment(order, payment_data):
        """Traiter le paiement d'une commande"""
        # Intégration avec Stripe ou autre processeur de paiement
        # :cite[3]:cite[6]
        try:
            # Simuler le traitement de paiement
            order.payment_status = 'paid'
            order.status = 'confirmed'
            order.save()
            
            return True
        except Exception as e:
            order.payment_status = 'failed'
            order.save()
            raise ValueError(f"Échec du paiement: {str(e)}")
            
    # views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import Product, Category, Cart, Order
from .services.cart_service import CartService
from .services.order_service import OrderService
import json

def home(request):
    """Page d'accueil de la boutique"""
    featured_products = Product.objects.filter(
        tenant=request.tenant,
        status='published'
    )[:8]
    
    context = {
        'featured_products': featured_products,
    }
    return render(request, 'store/home.html', context)

def product_list(request, category_slug=None):
    """Liste des produits"""
    category = None
    categories = Category.objects.filter(tenant=request.tenant)
    products = Product.objects.filter(tenant=request.tenant, status='published')
    
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug, tenant=request.tenant)
        products = products.filter(category=category)
    
    context = {
        'category': category,
        'categories': categories,
        'products': products,
    }
    return render(request, 'store/product_list.html', context)

def product_detail(request, slug):
    """Détail d'un produit"""
    product = get_object_or_404(
        Product, 
        slug=slug, 
        tenant=request.tenant, 
        status='published'
    )
    
    context = {
        'product': product,
    }
    return render(request, 'store/product_detail.html', context)

def cart_view(request):
    """Vue du panier"""
    cart = CartService.get_or_create_cart(request)
    
    context = {
        'cart': cart,
    }
    return render(request, 'store/cart.html', context)

@login_required
def checkout(request):
    """Processus de checkout"""
    cart = CartService.get_or_create_cart(request)
    
    if request.method == 'POST':
        try:
            billing_address = {
                'first_name': request.POST.get('billing_first_name'),
                'last_name': request.POST.get('billing_last_name'),
                'email': request.POST.get('billing_email'),
                'phone': request.POST.get('billing_phone'),
                'address': request.POST.get('billing_address'),
                'city': request.POST.get('billing_city'),
                'postal_code': request.POST.get('billing_postal_code'),
                'country': request.POST.get('billing_country'),
            }
            
            shipping_address = {
                'first_name': request.POST.get('shipping_first_name'),
                'last_name': request.POST.get('shipping_last_name'),
                'address': request.POST.get('shipping_address'),
                'city': request.POST.get('shipping_city'),
                'postal_code': request.POST.get('shipping_postal_code'),
                'country': request.POST.get('shipping_country'),
            }
            
            payment_method = request.POST.get('payment_method')
            
            order = OrderService.create_order_from_cart(
                cart, payment_method, billing_address, shipping_address
            )
            
            # Traiter le paiement
            if payment_method != 'cash':  # Paiement en ligne
                payment_result = OrderService.process_payment(order, {})
                if payment_result:
                    return redirect('order_detail', order_number=order.order_number)
            else:
                return redirect('order_detail', order_number=order.order_number)
                
        except ValueError as e:
            context = {
                'cart': cart,
                'error': str(e)
            }
            return render(request, 'store/checkout.html', context)
    
    context = {
        'cart': cart,
    }
    return render(request, 'store/checkout.html', context)

def order_detail(request, order_number):
    """Détail d'une commande"""
    order = get_object_or_404(Order, order_number=order_number, tenant=request.tenant)
    
    context = {
        'order': order,
    }
    return render(request, 'store/order_detail.html', context)

````
### Services de Vente sur Place et Facturation

````
# services/pos_service.py
from django.db import transaction
from django.utils import timezone
import uuid
from ..models import Product, Order, OrderItem, Inventory
from .inventory_service import InventoryService

class POSService:
    @staticmethod
    @transaction.atomic
    def create_pos_order(tenant, items, payment_method, customer_data=None):
        """Créer une commande en point de vente"""
        # Calculer les totaux
        subtotal = 0
        order_items = []
        
        for item in items:
            product = Product.objects.get(id=item['product_id'], tenant=tenant)
            variant = None
            if 'variant_id' in item:
                variant = product.variants.get(id=item['variant_id'])
            
            price = variant.price if variant else product.base_price
            quantity = item['quantity']
            
            subtotal += price * quantity
            
            order_items.append({
                'product': product,
                'variant': variant,
                'quantity': quantity,
                'price': price
            })
        
        tax_amount = subtotal * 0.2  # TVA
        total = subtotal + tax_amount
        
        # Créer la commande
        order = Order.objects.create(
            tenant=tenant,
            order_number=f"POS-{str(uuid.uuid4())[:8].upper()}",
            customer=None,  # Client anonyme en magasin
            payment_method=payment_method,
            billing_address=customer_data or {},
            shipping_address={},
            subtotal=subtotal,
            tax_amount=tax_amount,
            shipping_cost=0,
            total=total,
            status='confirmed',
            payment_status='paid'
        )
        
        # Créer les articles de commande et mettre à jour le stock
        for item_data in order_items:
            OrderItem.objects.create(
                order=order,
                product=item_data['product'],
                variant=item_data['variant'],
                quantity=item_data['quantity'],
                price=item_data['price']
            )
            
            # Mettre à jour le stock
            if item_data['product'].tracked:
                quantity_change = -item_data['quantity']
                InventoryService.update_inventory(
                    item_data['product'],
                    quantity_change,
                    'sold',
                    reason=f"Vente POS commande {order.order_number}",
                    reference=order.order_number
                )
        
        return order
    
    @staticmethod
    def search_products(tenant, query):
        """Rechercher des produits pour la caisse"""
        return Product.objects.filter(
            tenant=tenant,
            status='published',
            name__icontains=query
        ) | Product.objects.filter(
            tenant=tenant,
            status='published',
            description__icontains=query
        )
        
        
    # services/invoice_service.py
from django.template.loader import render_to_string
from weasyprint import HTML
from django.conf import settings
import os
from io import BytesIO
from django.core.files import File
from ..models import Invoice, Order
from .pos_service import POSService

class InvoiceService:
    @staticmethod
    def generate_invoice(order):
        """Générer une facture PDF pour une commande"""
        # Calculer les dates
        issued_at = timezone.now()
        due_date = issued_at + timezone.timedelta(days=30)
        
        # Créer la facture en base
        invoice = Invoice.objects.create(
            tenant=order.tenant,
            invoice_number=f"INV-{order.order_number}",
            order=order,
            issued_at=issued_at,
            due_date=due_date,
            amount=order.subtotal,
            tax_amount=order.tax_amount,
            total=order.total
        )
        
        # Générer le PDF
        context = {
            'invoice': invoice,
            'order': order,
            'tenant': order.tenant,
        }
        
        html_string = render_to_string('store/invoice_template.html', context)
        html = HTML(string=html_string, base_url=settings.BASE_URL)
        
        # Sauvegarder le PDF
        pdf_bytes = html.write_pdf()
        pdf_file = BytesIO(pdf_bytes)
        
        invoice.pdf_file.save(
            f"invoice_{invoice.invoice_number}.pdf",
            File(pdf_file)
        )
        invoice.save()
        
        return invoice
    
    @staticmethod
    def get_invoice_pdf(invoice_id):
        """Obtenir le fichier PDF de la facture"""
        invoice = Invoice.objects.get(id=invoice_id)
        return invoice.pdf_file
        
        
        
    # views.py (suite)
@login_required
def pos_dashboard(request):
    """Tableau de bord de la caisse enregistreuse"""
    if not request.user.has_perm('store.can_use_pos'):
        return redirect('home')
    
    context = {
        'recent_orders': Order.objects.filter(
            tenant=request.tenant
        ).order_by('-created_at')[:10]
    }
    return render(request, 'store/pos/dashboard.html', context)

@login_required
def pos_search_products(request):
    """Recherche de produits pour la caisse"""
    query = request.GET.get('q', '')
    products = POSService.search_products(request.tenant, query)
    
    results = []
    for product in products:
        results.append({
            'id': product.id,
            'name': product.name,
            'price': float(product.base_price),
            'in_stock': product.in_stock,
            'image_url': product.main_image.url if product.main_image else None
        })
    
    return JsonResponse({'products': results})

@login_required
@csrf_exempt
def pos_create_order(request):
    """Créer une commande depuis la caisse"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            items = data.get('items', [])
            payment_method = data.get('payment_method', 'cash')
            customer_data = data.get('customer_data', {})
            
            order = POSService.create_pos_order(
                request.tenant, items, payment_method, customer_data
            )
            
            # Générer la facture
            invoice = InvoiceService.generate_invoice(order)
            
            return JsonResponse({
                'success': True,
                'order_number': order.order_number,
                'invoice_number': invoice.invoice_number
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)

@login_required
def pos_print_invoice(request, order_number):
    """Imprimer une facture"""
    order = get_object_or_404(Order, order_number=order_number, tenant=request.tenant)
    invoice = getattr(order, 'invoice', None)
    
    if not invoice:
        invoice = InvoiceService.generate_invoice(order)
    
    pdf_file = InvoiceService.get_invoice_pdf(invoice.id)
    
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="facture_{invoice.invoice_number}.pdf"'
    return response
    
    

````