from rest_framework import serializers

from stocks.models import Category, Unity, Brands, Product


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class CategoryNameSlugIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id','slug','name']


class UnitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Unity
        fields = '__all__'

class UnityCodeNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unity
        fields = ['id','code','name']

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brands
        fields = '__all__'

class ProductListSerializer(serializers.ModelSerializer):
    category=CategoryNameSlugIdSerializer()
    unity=UnityCodeNameSerializer()
    class Meta:
        model = Product
        fields = ['id', 'name','description', 'slug', 'identity','category', 'salePrice', 'unity','is_promo','promo_percent','image', 'outStock','initialStock', 'status']