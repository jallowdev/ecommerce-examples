from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from stocks.models import Product, Category, Unity


class ProductResource(resources.ModelResource):
    class Meta:
        model = Product
        fields = ('id', 'name', 'description', 'category', 'unity', 'price', 'salePrice', 'initialStock')
        import_id_fields = ('id',)
        skip_unchanged = True


class CategoryResource(resources.ModelResource):
    class Meta:
        model = Category
        fields = ('id', 'name')
        import_id_fields = ('id',)
        skip_unchanged = True


class UnityResource(resources.ModelResource):
    class Meta:
        model = Unity
        fields = ('id', 'code', 'name')
        import_id_fields = ('id',)
        skip_unchanged = True


@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin):
    resource_class = ProductResource

    list_display = ('id', 'identity', 'name', 'description', 'category__name', 'unity__name', 'price', 'salePrice',
                    'initialStock', 'disponibility', 'status')
    list_filter = ('name', 'category__name')


@admin.register(Category)
class CategoryAdmin(ImportExportModelAdmin):
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
