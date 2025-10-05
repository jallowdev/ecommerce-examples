from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponse
from django.template import loader
from django.urls import path, include

from core import settings


def index_ecom(request):
    context = {'segment': 'index'}

    html_template = loader.get_template('ecom/home/home.html')
    return HttpResponse(html_template.render(context, request))


urlpatterns = [
    path('admin/', admin.site.urls),
    path('ecom/', index_ecom, name='index_ecom'),
    path('cosmos/', include('cosmos.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = 'TECH-COSMETIQUE ADMIN'
admin.site.index_title = 'Services'
admin.site.site_title = 'STOCK COSMETIQUE API'
