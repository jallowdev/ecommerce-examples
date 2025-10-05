# Create your models here.
import uuid

from django.contrib.auth.models import AbstractUser, Group
from django.db import models
from django.utils import timezone

from core.commons.commons import STATUS, generate_slug

STATUSUSER = {
    ('ENABLE', 'Active'),
    ('PENDING', 'En cours'),
    ('CANCELLED', 'Supprimé'),
    ('DISABLE', 'Disable'),
    ('PENDING_KYC', 'Demande Kcy'),
    ('VALID_KYC', 'Valider Kcy'),
    ('REJECT_KYC', 'Rejeter Kyc'),
}

ROLE = {
    ('ADMIN_SYSTEM', 'Super Admin'),
    ('SUPERVISOR_SYSTEM', 'Superviseur System'),
    ('TRESORIER_SYSTEM', 'Tresorier System'),
    ('SUPPORT_SYSTEM', 'Support System'),
    ('FOURNISSEUR', 'Fournisseur'),
    ('ADMIN_PARTNER', 'Administrateur partenaire'),
    ('CHEF_BOUTIQUE', 'Chef Boutique'),
    ('SUPERVISOR', 'Superviseur'),
    ('AGENT_CAISSE', 'Agent Caisse'),
    ('AGENT_CONTROLE', 'Agent Controle'),
    ('SUPPORT', 'Support'),
    ('CUSTOMER_INVOICE', 'Client Boutique'),
    ('CUSTOMER', 'Client'),
}
ROLE_FORM = {
    ('ADMIN_MAGASIN', 'Administrateur Magasin'),
    ('CHEF_BOUTIQUE', 'Chef Boutique'),
    ('SUPERVISOR', 'Superviseur'),
    ('AGENT_CAISSE', 'Agent Caisse'),
    ('AGENT_CONTROLE', 'Agent Controle'),
    ('SUPPORT', 'Support')
}

ROLE_FORM_PARTNER = {
    'ADMIN_PARTNER': 'Administrateur partenaire',
    'CHEF_BOUTIQUE': 'Chef Boutique',
    'SUPERVISOR': 'Superviseur',
    'AGENT_CAISSE': 'Agent Caisse'
}
ENUM_EMPTY = {}
ROLE_FORM1 = [
    ('ADMIN_MAGASIN', 'Administrateur Magasin'),
    ('CHEF_BOUTIQUE', 'Chef Boutique'),
    ('SUPERVISOR', 'Superviseur'),
    ('AGENT_CAISSE', 'Agent Caisse'),
    ('AGENT_CONTROLE', 'Agent Controle'),
    ('SUPPORT', 'Support'),
]

FUNCTIONALITY = {
    'DASHBOARD': 'Dashboard',
    'CUSTOMERS': 'Compte Clients',
    'ENTITIES': 'Entités',
    'USERS': 'Utilisateurs',
    'STOCKS': 'Stocks',
    'SALES': 'Ventes',
    'PURCHASES': 'Achats',
    'MARKETING': 'Communications',
    'SETTINGS': 'Parametrages',
}

ENTITYTYPE = {
    'RACINE': 'Racine',
    'FOURNISSEUR': 'Fournisseur',
    # 'PARTNER': 'Partenaire',
    'BOUTIQUE': 'Boutique',
    'CAISSE': 'Caisse',
    'UNIVERSITY': 'Université',
    'SCHOOL': 'École',
    'CORPORATE': 'Entreprise',
    'INSTITUTION': 'Institution publique',
}
GENRE = {
    'M': 'Masculin',
    'F': 'Feminin',
    'I': 'Inconnue'
}

STATUSSESSION = {
    'OPEN': 'Ouverte',
    'CLOSE': 'Fermée',
}
USERKYCDOCTYPE = {
    'PASSPORT': 'Passeport',
    'CNI': "Carte d Identité",
}


class User(AbstractUser):
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
    identity = models.UUIDField(unique=True, null=False, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=50, default='')
    phone = models.CharField(max_length=50, default="", blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    entity = models.ForeignKey('Entity', related_name="users_entity", on_delete=models.SET_NULL, null=True)
    address = models.ForeignKey('Address', related_name="users_address", on_delete=models.SET_NULL, null=True)
    profile = models.OneToOneField('Profile', related_name="users_profile", on_delete=models.SET_NULL, null=True)

    status = models.CharField(max_length=50, choices=STATUSUSER, default='ENABLE')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    segment = models.CharField(max_length=20, choices=SEGMENT_CHOICES, blank=True)
    is_email_verify = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.email}, {self.first_name} "

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"


class AuditFieldsModel(models.Model):
    #identity = models.UUIDField(unique=True, null=False, default=uuid.uuid4, editable=False)
    identity = models.CharField(unique=True, null=False, default=str(uuid.uuid4)[:10], editable=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, related_name="%(class)s_created_by", on_delete=models.SET_NULL,
                                   null=True)
    updated_by = models.ForeignKey(User, related_name="%(class)s_updated_by", on_delete=models.SET_NULL,
                                   null=True)
    status = models.CharField(max_length=50, choices=STATUS, default='ENABLE')

    class Meta:
        abstract = True
        ordering = ['-created_at']


class Functionality(models.Model):
    code = models.CharField(max_length=50, primary_key=True, choices=FUNCTIONALITY)
    libelle = models.CharField(max_length=80, default='')
    icon = models.CharField(max_length=80, default='')
    url = models.CharField(max_length=80, default='')
    parent = models.ForeignKey('self', related_name='functionalityParent', on_delete=models.SET_NULL, null=True)
    roles = models.ManyToManyField(Group, related_name="fonctionnalites", blank=True)
    status = models.CharField(max_length=50, choices=STATUS, default='ENABLE')
    orderby = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.code}, {self.libelle} , {self.parent} "

    @property
    def child_list(self):
        return self.objects.all()

    class Meta:
        verbose_name_plural = "Functionalities"


class Address(models.Model):
    country = models.CharField(max_length=100, default="")
    city = models.CharField(max_length=100, default="")
    state = models.CharField(max_length=100, default="")
    street = models.CharField(max_length=100, default="")

    location = models.CharField(max_length=250, default="")

    longitude = models.CharField(max_length=100, blank=True, default="")
    latitude = models.CharField(max_length=100, blank=True, default="")

    def __str__(self):
        return f" {self.id}, {self.country}, {self.city} "

    class Meta:
        verbose_name_plural = "Address"


class PartnerInfo(models.Model):
    address = models.ForeignKey(Address, related_name='entity_address', on_delete=models.SET_NULL, null=True)
    ninea = models.CharField(max_length=40, default='', blank=True)
    phone = models.CharField(max_length=20, default='', blank=True)
    email = models.EmailField(blank=True, default='', )
    logo = models.URLField(blank=True, default='', )
    logoTicket = models.URLField(blank=True, default='', )
    website = models.URLField(blank=True, default='', )

    first_color = models.CharField(max_length=20, blank=True, default='', )
    second_color = models.CharField(max_length=20, blank=True, default='', )
    third_color = models.CharField(max_length=20, blank=True, default='', )

    domain = models.CharField(max_length=100, unique=True)
    theme = models.JSONField(default=dict)

    def __str__(self):
        return f" {self.pk}, {self.phone} "

    class Meta:
        verbose_name_plural = "PartnerInfos"


class Entity(AuditFieldsModel):
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=80)
    subtitle = models.CharField(default="", max_length=100)
    entitytype = models.CharField(max_length=80, choices=ENTITYTYPE)
    parent = models.ForeignKey('self', related_name='entityParent', on_delete=models.SET_NULL, null=True)
    infos = models.ForeignKey(PartnerInfo, related_name='entities', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f" {self.pk}, {self.title}, {self.entitytype} "

    @property
    def products(self):
        return self.products_store.all()

    class Meta:
        verbose_name_plural = "Entitées"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_slug(self.title, str(self.identity)[:8])
        super().save(*args, **kwargs)


class Profile(models.Model):
    kycDocType = models.CharField(max_length=20, choices=USERKYCDOCTYPE, default='CNI')
    profileLink = models.CharField(max_length=255, default="", blank=True)
    facebookLink = models.CharField(max_length=255, default="", blank=True)
    instagramLink = models.CharField(max_length=255, default="", blank=True)
    rectoLink = models.CharField(max_length=255, default="", blank=True)
    versoLink = models.CharField(max_length=255, default="", blank=True)
    selfieLink = models.CharField(max_length=255, default="", blank=True)
    passportLink = models.CharField(max_length=255, default="", blank=True)
    gender = models.CharField(max_length=25, choices=GENRE, default="I", blank=True)

    def __str__(self):
        return f" {self.pk}, {self.gender} "

    class Meta:
        verbose_name_plural = "Profiles"


class AuthSession(models.Model):
    APP_TYPES = [
        ('WEB', 'Web'),
        ('TPE', 'Terminal de paiement'),
        ('MOBILE', 'Mobile'),
        ('DESKTOP', 'Ordinateur fixe'),
    ]
    user = models.ForeignKey('User', related_name="user_sessions", on_delete=models.SET_NULL, null=True)
    token = models.TextField(default="")
    refresh = models.TextField(default="")

    login_at = models.DateTimeField(default=timezone.now)
    logout_at = models.DateTimeField(auto_now=True)

    app = models.CharField(max_length=50, choices=APP_TYPES, default='WEB')

    status = models.CharField(max_length=50, choices=STATUSSESSION, default='OPEN')

    def __str__(self):
        return f" SESSION : {self.user.first_name} / {self.user.last_name} / {self.user.created_at}"

    class Meta:
        verbose_name_plural = "Sessions"
