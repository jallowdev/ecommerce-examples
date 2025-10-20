from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q

from stocks.models import Brands, Category, Unity, Product
from users.models import Entity


class ProductForm(forms.Form):
    unity = forms.ChoiceField(
        choices=[],
        label="Choisissez votre l'unité",
        widget=forms.Select(
            attrs={
                "placeholder": "Choisissez l'unité",
                "class": "form-control"
            }
        ))
    category = forms.ChoiceField(
        choices=[],
        label="Choisissez votre l'unité",
        widget=forms.Select(
            attrs={
                "placeholder": "Choisissez la marque",
                "class": "form-control"
            }
        ))
    brand = forms.ChoiceField(
        choices=[],
        label="Choisissez votre l'unité",
        widget=forms.Select(
            attrs={
                "placeholder": "Choisissez la marque",
                "class": "form-control"
            }
        ))
    store = forms.ChoiceField(
        choices=[],
        label="Choisissez votre l'unité",
        widget=forms.Select(
            attrs={
                "placeholder": "Choisissez la marque",
                "class": "form-control"
            }
        ))
    images = forms.FileField(
        widget=forms.ClearableFileInput(
            attrs={
                "placeholder": "Telechargez les images",
                "class": "form-control",
                "multipe": True
            }
        ))
    description = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Description",
                "class": "form-control"
            }
        ))
    name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Libelle",
                "class": "form-control"
            }
        ))
    price = forms.DecimalField(
        label='Prix Unitaire',
        max_digits=10,
        decimal_places=2,
        required=True,
        error_messages={
            'required': 'Ce champ est requis.',
            'invalid': 'Veuillez entrer un montant valide.'
        },
        widget=forms.NumberInput(
            attrs={
                "placeholder": "000 000 XOF",
                "class": "form-control"
            }
        )
    )

    salePrice = forms.DecimalField(
        label='Prix Vente',
        max_digits=10,
        decimal_places=2,
        required=True,
        error_messages={
            'required': 'Ce champ est requis.',
            'invalid': 'Veuillez entrer un montant valide.'
        },
        widget=forms.NumberInput(
            attrs={
                "placeholder": "000 000 XOF",
                "class": "form-control"
            }
        )
    )

    initialStock = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={
                "placeholder": "Stock initial",
                "class": "form-control"
            }
        ))

    def clean_images(self):
        images = self.cleaned_data.get('images', False)
        if images:
            if images.size > 4 * 1024 * 1024:  # 4MB max
                raise ValidationError("L'image est trop grande (max 4MB)")
            return images
        raise ValidationError("Impossible de lire l'image uploadée")

    def __init__(self, role=None, parent_id=None, *args, **kwargs):
        super().__init__()
        self.fields['category'].choices = [(category.pk, category.name) for category in
                                           Category.objects.exclude(status='CANCEL')]
        self.fields['brand'].choices = [(b.pk, b.name) for b in Brands.objects.exclude(status='CANCEL')]
        self.fields['unity'].choices = [(b.pk, b.name) for b in Unity.objects.exclude(status='CANCEL')]
        if parent_id and role != 'ADMIN_SYSTEM':
            self.fields['store'].choices = [(b.pk, b.title) for b in
                                            Entity.objects.filter(Q(pk=parent_id) | Q(parent__pk=parent_id)).filter(
                                                entitytype='BOUTIQUE').exclude(status='CANCEL').all()]
        else:
            self.fields['store'].choices = [(b.pk, b.title) for b in
                                            Entity.objects.filter(entitytype='BOUTIQUE').exclude(status='CANCEL').all()]


class ProductModelForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "__all__"

    unity = forms.ChoiceField(
        choices=[],
        label="Choisissez votre l'unité",
        widget=forms.Select(
            attrs={
                "placeholder": "Choisissez l'unité",
                "class": "form-control"
            }
        ))
    category = forms.ChoiceField(
        choices=[],
        label="Choisissez votre l'unité",
        widget=forms.Select(
            attrs={
                "placeholder": "Choisissez la marque",
                "class": "form-control"
            }
        ))
    brand = forms.ChoiceField(
        choices=[],
        label="Choisissez votre l'unité",
        widget=forms.Select(
            attrs={
                "placeholder": "Choisissez la marque",
                "class": "form-control"
            }
        ))
    images = forms.FileField(
        widget=forms.ClearableFileInput(
            attrs={
                "placeholder": "Telechargez les images",
                "class": "form-control",
                "multipe": True
            }
        ))

    description = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Description",
                "class": "form-control"
            }
        ))
    name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Libelle",
                "class": "form-control"
            }
        ))
    price = forms.DecimalField(
        label='Prix Unitaire',
        max_digits=10,
        decimal_places=2,
        required=True,
        error_messages={
            'required': 'Ce champ est requis.',
            'invalid': 'Veuillez entrer un montant valide.'
        },
        widget=forms.NumberInput(
            attrs={
                "placeholder": "000 000 XOF",
                "class": "form-control"
            }
        )
    )

    salePrice = forms.DecimalField(
        label='Prix Vente',
        max_digits=10,
        decimal_places=2,
        required=True,
        error_messages={
            'required': 'Ce champ est requis.',
            'invalid': 'Veuillez entrer un montant valide.'
        },
        widget=forms.NumberInput(
            attrs={
                "placeholder": "000 000 XOF",
                "class": "form-control"
            }
        )
    )

    initialStock = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={
                "placeholder": "Stock initial",
                "class": "form-control"
            }
        ))
