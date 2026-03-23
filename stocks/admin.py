from django import forms
from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin, ExportActionMixin

from stocks.models import Product, Category, Unity, StockImage


class ProductResource(resources.ModelResource):
    class Meta:
        model = Product
        fields = ('id', 'identity','name', 'description', 'category', 'unity', 'price', 'salePrice', 'initialStock','default_image')
        import_id_fields = ('id',)
        skip_unchanged = True


class CategoryResource(resources.ModelResource):
    class Meta:
        model = Category
        fields = ('id', 'name','parent')
        import_id_fields = ('id',)
        skip_unchanged = True


class UnityResource(resources.ModelResource):
    class Meta:
        model = Unity
        fields = ('id', 'code', 'name')
        import_id_fields = ('id',)
        skip_unchanged = True


class ProductAdminForm(forms.ModelForm):
    banner = forms.FileField(required=False, label='Image du banniere')
    image_gm = forms.FileField(required=False, label='Image gm du produit')
    image_pm = forms.FileField(required=False, label='Image pm du produit')

    class Meta:
        model = Product
        fields = '__all__'



@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin, ExportActionMixin,admin.ModelAdmin):
    resource_class = ProductResource

    list_display = ('id', 'identity', 'name', 'description', 'category__name', 'unity__name', 'price', 'salePrice',
                    'initialStock', 'disponibility', 'status')
    list_filter = ('name', 'category__name')
    #search_fields = ('name',)

    form = ProductAdminForm

    def save_model(self, request, obj, form, change):
        # Récupère le fichier uploadé depuis le formulaire
        banner = form.cleaned_data.get('banner')
        banner_url = ''
        image_gm = form.cleaned_data.get('image_gm')
        image_gm_url = ''
        image_pm = form.cleaned_data.get('image_pm')
        image_pm_url = ''

        if banner:
            from core.commons.firebase_service import save_file
            path_firebase = 'cosmos/products/'
            url = save_file(path_firebase, banner)
            banner_url = url

        if image_gm:
            from core.commons.firebase_service import save_file
            path_firebase = 'cosmos/products/'
            url = save_file(path_firebase, image_gm)
            image_gm_url = url

        if image_pm:
            from core.commons.firebase_service import save_file
            path_firebase = 'cosmos/products/'
            url = save_file(path_firebase, image_pm)
            image_pm_url = url
        img=StockImage.objects.create(banner=banner_url,image_gm=image_gm_url,image_pm=image_pm_url)



        super().save_model(request, obj, form, change)



@admin.register(Category)
class CategoryAdmin(ImportExportModelAdmin, ExportActionMixin):
    resource_class = CategoryResource

    list_display = ('id', 'name', 'parent__name', 'status')


@admin.register(Unity)
class UnityAdmin(ImportExportModelAdmin):
    resource_class = UnityResource

    list_display = ('id', 'code', 'name', 'status')


'''

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

'''
