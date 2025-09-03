import uuid
from typing import Optional

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone

from core.commons.commons import generate_slug
from users.models import AuditFieldsModel, Entity

CATEGORY = {
    'CATEGORY': 'Categorie',
    'SUBCATEGORY': 'Sous Categorie',
}


class Category(AuditFieldsModel):
    name = models.CharField(max_length=80)
    categoryType = models.CharField(max_length=80, choices=CATEGORY, default='CATEGORY')
    logo = models.FileField(upload_to='media/categories/')
    parent = models.ForeignKey('self', related_name='CategoryParent', on_delete=models.SET_NULL, null=True)
    slug = models.SlugField(unique=True, null=False, blank=True)
    store = models.ForeignKey(Entity, related_name='categories_store', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f" {self.identity}, {self.name}, {self.categoryType} "

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['slug']),
        ]


    def get_absolute_url(self):
        return reverse("category_detail", kwargs={"slug": self.slug})


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_slug(self.name, str(self.identity)[:8])
        super().save(*args, **kwargs)


class Brands(AuditFieldsModel):
    name = models.CharField(max_length=80)
    logo = models.FileField(upload_to='media/brands/')
    slug = models.SlugField(unique=True, null=False, blank=True)
    store = models.ForeignKey(Entity, related_name='brands_store', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f" {self.identity}, {self.name}"

    class Meta:
        verbose_name = "Brand"
        verbose_name_plural = "Brands"
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['slug']),
        ]

    def get_absolute_url(self):
        return reverse("brand_detail", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_slug(self.name, str(self.identity)[:8])
        super().save(*args, **kwargs)


class Unity(AuditFieldsModel):
    name = models.CharField(max_length=80)
    code = models.CharField(default=str(uuid.uuid4), unique=True, max_length=100)
    slug = models.CharField(max_length=50, default="")

    def __str__(self):
        return f" {self.identity}, {self.name}"

    class Meta:
        verbose_name_plural = "Unities"


class Product(AuditFieldsModel):

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

    name = models.CharField(max_length=150)
    description = models.TextField(default="")
    slug = models.SlugField(unique=True, null=False, blank=True)
    qrcode = models.TextField(default="", null=False)

    store = models.ForeignKey(Entity, related_name='products_store', on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey(Category, related_name='categories', on_delete=models.SET_NULL, null=True)
    unity = models.ForeignKey(Unity, related_name='unities', on_delete=models.SET_NULL, null=True)
    brand = models.ForeignKey(Brands, related_name='brands', on_delete=models.SET_NULL, null=True)

    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    salePrice = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    minStock = models.IntegerField(default=0)
    initialStock = models.IntegerField(default=0)

    inStock = models.IntegerField(default=0)

    outStock = models.IntegerField(default=0)

    alert_threshold = models.IntegerField(default=10)
    expiration_date = models.DateField(null=True)
    entrepot_address = models.CharField(max_length=20, default='')

    disponibility = models.CharField(max_length=20, choices=DISPONIBILITE_CHOICES, default='en_stock')
    badges = models.JSONField(default=list, blank=True)
    specifications = models.JSONField(default=dict)
    images = models.JSONField(default=list)

    # SEO
    meta_title = models.CharField(max_length=100, blank=True)
    meta_description = models.TextField(blank=True)

    @property
    def recto(self)->Optional[str]:
        if len(self.product_images.all()):
            return self.product_images.all()[0].url
        return ''

    @property
    def current_stock(self)-> int:
        return self.initialStock - self.outStock

    @property
    def is_alert(self):
        return self.current_stock <= self.alert_threshold

    @property
    def total(self):
        return int(self.price * self.current_stock)

    @property
    def get_price(self):
        return int(self.price)

    @property
    def get_sale_price(self):
        return int(self.salePrice)

    @property
    def total_sale_price(self):
        return int(self.salePrice * self.current_stock)

    def __str__(self):
        return f" {self.pk} - {self.identity} - {self.name} - {self.price} - {self.salePrice}"

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['name', 'category','brand']),
            models.Index(fields=['price']),
            models.Index(fields=['slug']),
            models.Index(fields=['store']),
        ]

    def get_absolute_url(self):
        return reverse("product_detail", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_slug(self.name, str(self.identity)[:8])
        super().save(*args, **kwargs)

class StockMov(AuditFieldsModel):
    """Historique des mouvements de stock"""
    ACTION_CHOICES = (
        ('in', 'Entrée'),
        ('out', 'Sortie'),
        ('adjust', 'Ajustement'),
        ('sold', 'Vente'),
        ('return', 'Retour'),
    )

    inventory = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='products_movement')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    quantity = models.IntegerField()
    previous_quantity = models.IntegerField()
    new_quantity = models.IntegerField()
    reason = models.TextField(blank=True)
    reference = models.CharField(max_length=100, blank=True)


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='product_images', on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=80)
    url = models.TextField(default='', max_length=300)

    class Meta:
        verbose_name_plural = "Image products"



class Avis(AuditFieldsModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='avis')
    note = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    comment = models.TextField(default='')
    is_approve = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Avis"
        verbose_name_plural = "Avis"
        unique_together = ['produit', 'auteur']

    def __str__(self):
        return f"Avis de {self.created_by.username} sur {self.product.name}"



class Promotion(AuditFieldsModel):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    type_promotion = models.CharField(max_length=20, choices=[
        ('pourcentage', 'Pourcentage'),
        ('montant_fixe', 'Montant fixe'),
        ('livraison_gratuite', 'Livraison gratuite'),
    ])
    value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    products = models.ManyToManyField(Product, blank=True)
    categories = models.ManyToManyField(Category, blank=True)
    date_debut = models.DateTimeField(auto_now=True)
    date_fin = models.DateTimeField()
    is_enable = models.BooleanField(default=True)
    segments_cibles = models.JSONField(default=list, blank=True)
    store = models.ForeignKey(Entity, related_name='promotion_store', on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['-date_debut']

    def __str__(self):
        return self.name

    def est_active(self):
        maintenant = timezone.now()
        return self.is_enable and self.date_debut <= maintenant <= self.date_fin

