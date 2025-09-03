from django.core.validators import MinValueValidator
from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse

from core.commons.commons import STATUS
from stocks.models import Product
from users.models import AuditFieldsModel, User, Entity, Address

INVOICE_STATUS = {
    'PENDING': 'En cours',
    'UNPAID': 'Non payée',
    'PAID': 'Payé',
    'ORDER': 'Commande',
    'PROFORMA': 'Proforma',
    'RECEIVED': 'Livrée',
    'COMPETED': 'Completée',
    'ARCHIVE': 'Archivée',
    'CANCEL': 'Supprimée'
}
PAYMENT_STATUS = {
    'UNPAID': 'Non payé',
    'PAID': 'Payé',
    'PARTIAL': 'Partiel',
    'DUE': 'Restant',
    'ARCHIVE': 'Archivé',
    'CANCEL': 'Supprimé'
}


class Payment(models.Model):
    MODE_PAIEMENT_CHOICES = [
        ('orange_money', 'Orange Money'),
        ('wave', 'Wave'),
        ('carte_credit', 'Carte de crédit'),
        ('virement', 'Virement bancaire'),
        ('especes', 'Paiement en espèces'),
    ]
    name = models.CharField(max_length=80)
    code = models.CharField(choices=MODE_PAIEMENT_CHOICES, max_length=100)
    icon = models.CharField(default="", max_length=250)
    status = models.CharField(max_length=50, choices=STATUS, default='ENABLE')

    def __str__(self):
        return f" {self.code}, {self.name}"

    class Meta:
        verbose_name_plural = "payments"


class QRCode(models.Model):
    content = models.CharField(max_length=55, verbose_name="Contenu du QR Code", default='')
    url = models.TextField(verbose_name="image_urls", default='')
    image = models.ImageField(upload_to='qrcodes/', null=True)


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Panier"
        verbose_name_plural = "Paniers"

    def __str__(self):
        if self.user:
            return f"Panier de {self.user.username}"
        return f"Panier session {self.session_key}"

    def get_total(self):
        return sum(item.get_sous_total() for item in self.items.all())

    def get_nombre_items(self):
        return sum(item.quantity for item in self.items.all())


class ItemCart(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Item cart"
        verbose_name_plural = "Items cart"
        unique_together = ['cart', 'product']

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    def get_sous_total(self):
        return self.product.get_sale_price * self.quantity


class Invoice(AuditFieldsModel):
    slug = models.SlugField(unique=True, null=False, blank=True)

    customer = models.ForeignKey(User, related_name="customers", on_delete=models.SET_NULL, null=True)
    biller = models.ForeignKey(User, related_name="billers", on_delete=models.SET_NULL, null=True)
    qrcode = models.OneToOneField(QRCode, related_name="qrcode", on_delete=models.SET_NULL, null=True, blank=True)

    invoiceStatus = models.CharField(max_length=50, choices=INVOICE_STATUS, default='UNPAID')
    paymentStatus = models.CharField(max_length=50, choices=PAYMENT_STATUS, default='UNPAID')
    payed_at = models.DateTimeField(null=True, blank=True)

    printCounter = models.IntegerField(default=0)

    store = models.ForeignKey(Entity, related_name='invoices_store', on_delete=models.PROTECT, null=True)

    @property
    def details(self):
        return self.invoice_sales.all()

    @property
    def quantity(self):
        return sum([n.quantity for n in self.invoice_sales.all() if n.status == 'ENABLE'])

    @property
    def payments(self) -> list:
        return [n for n in self.invoice_orders.all() if n.status == 'ENABLE']

    @property
    def total_payment(self):
        if len(self.invoice_orders.all()) == 0:
            return 0
        return sum([n.amount for n in self.invoice_orders.all() if n.status == 'ENABLE'])

    @property
    def total(self):
        if len(self.invoice_sales.all()) == 0:
            return 0
        return int(sum([line.sub_total for line in self.invoice_sales.all()]))

    @property
    def pay_due(self):
        return int(self.total - self.total_payment)

    @property
    def amount_pay(self):
        if not len(self.invoice_orders.all()):
            return 0
        return int(sum([line.amount for line in self.invoice_orders.all()]))

    @property
    def amount_due(self):
        return int(self.total - self.amount_pay)

    def __str__(self):
        return f" FACTURE - {self.identity}"

    def get_absolute_url(self):
        return reverse("facture_pt_detail", kwargs={"pk": self.identity})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f'invoice-{self.identity}')

        if not self.qrcode:
            self.qrcode = self.identity

        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Invoices"


class Order(AuditFieldsModel):
    SOURCE_CHOICES = [
        ('ECOM', 'E-commerce'),
        ('POS', 'Point de Vente'),
    ]
    STATUS_CHOICES = (
        ('pending', 'En attente'),
        ('confirmed', 'Confirmée'),
        ('processing', 'En traitement'),
        ('shipped', 'Expédiée'),
        ('delivered', 'Livrée'),
        ('cancelled', 'Annulée'),
        ('refunded', 'Remboursée'),
    )

    PAYMENT_STATUS_CHOICES = (
        ('pending', 'En attente'),
        ('paid', 'Payée'),
        ('failed', 'Échouée'),
        ('refunded', 'Remboursée'),
    )

    store = models.ForeignKey(Entity, related_name='orders_store', on_delete=models.PROTECT)
    source = models.CharField(max_length=4, choices=SOURCE_CHOICES)

    invoice = models.ForeignKey(Invoice, related_name='invoice_orders', on_delete=models.SET_NULL, null=True)
    phoneNumber = models.CharField(max_length=80, db_column='telephone', blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment = models.ForeignKey(Payment, related_name='payments', on_delete=models.SET_NULL, null=True)

    delivery_address = models.ForeignKey(Address, on_delete=models.PROTECT, related_name='delivery_address')
    bill_address = models.ForeignKey(Address, on_delete=models.PROTECT, related_name='commandes_facturation')
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_fees = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    note = models.TextField(blank=True, default="")
    order_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f" {self.pk}, {self.payment.name}"

    class Meta:
        db_table = 'command'
        verbose_name_plural = "commands"


class Sale(AuditFieldsModel):
    invoice = models.ForeignKey(Invoice, related_name='invoice_sales', on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(Product, related_name='product_sale', on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    @property
    def sub_total(self):
        return int(self.price * self.quantity)

    @property
    def get_price(self):
        return int(self.price)

    def __str__(self):
        return f" {self.pk}-{self.product.name}-{self.price}"

    class Meta:
        db_table = 'sale'
        verbose_name_plural = "sales"
