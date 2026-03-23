from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from stocks.models import Category, Unity, Product
from stocks.serializers import CategorySerializer, ProductListSerializer, UnitySerializer


class CategoryController(ReadOnlyModelViewSet):
    queryset = Category.objects.filter(status='ENABLE').order_by('pk')
    serializer_class = CategorySerializer
    lookup_field = 'slug'

    @action(detail=True, methods=['get'])
    def products(self, request, slug=None):

        """Récupère tous les produits d'une catégorie"""
        category = Category.objects.filter(status='ENABLE',slug=slug).first()
        products=category.get_products

        # Filtrage avancé
        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')

        if min_price:
            products = products.filter(price__gte=min_price)
        if max_price:
            products = products.filter(price__lte=max_price)

        page = self.paginate_queryset(products)
        if page is not None:
            serializer = ProductListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = ProductListSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def get_subcategories(self, request, slug=None):
        """Récupère les sous-catégories d'une catégorie"""

        subcategories = Category.objects.filter(parent__slug=slug, status='ENABLE').order_by('pk')
        page = self.paginate_queryset(subcategories)
        if page is not None:
            serializer = CategorySerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = CategorySerializer(subcategories, many=True, context={'request': request})
        return Response(serializer.data)


class UnityController(ModelViewSet):
    queryset = Unity.objects.all()
    serializer_class = UnitySerializer


class ProductController(ReadOnlyModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductListSerializer


def is_integer(value):
    try:
        int(value)
        return True
    except (ValueError, TypeError):
        return False


"""
router.register(r'categories', CategoryViewSet, basename='category')


"""
