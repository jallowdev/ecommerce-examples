from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework.routers import DefaultRouter

from core import settings
from stocks.api.product_controller import ProductController, UnityController, CategoryController
from stocks.models import Category

schema_view = get_schema_view(
    openapi.Info(
        title="OUDIA API",
        default_version='v1',
        description="SERVICES MANAGEMENT STOCK AND ECOMMERCE",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@tin.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


router = DefaultRouter()
router.register(r"products", ProductController, basename="products")
router.register(r"categories", CategoryController, basename="categories")
router.register(r"unities", UnityController, basename="unities")


urlpatterns = [
    path('api/swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    path('api/', include(router.urls)),


    path('admin/', admin.site.urls),
    path('cosmos/', include('cosmos.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = 'COSMETIQUE ADMIN'
admin.site.index_title = 'Services'
admin.site.site_title = 'STOCK COSMETIQUE API'
