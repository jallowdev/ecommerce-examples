from django.urls import path

from stocks.products.product_views import product_by_category_list_home, product_list_home, category_list_home

urlpatterns = [
    path('<int:category_id>/', product_by_category_list_home, name='product_by_category_list_home'),
    path('products/', product_list_home, name='product_list_home'),
    path('categories/', category_list_home, name='category_list_home'),
]
