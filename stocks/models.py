import uuid
from typing import Optional

from django.db import models
from django.urls import reverse

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
    name = models.CharField(max_length=80)
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

    store = models.ForeignKey(Entity, on_delete=models.PROTECT, related_name='store_products', null=True)

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

    """
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f'{self.name}-{self.category.name}-{self.unity.name}-{self.identity}')
        super().save(*args, **kwargs)
    """

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_slug(self.name, str(self.identity)[:8])
        super().save(*args, **kwargs)


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='product_images', on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=80)
    url = models.TextField(default='', max_length=300)

    class Meta:
        verbose_name_plural = "Image products"
