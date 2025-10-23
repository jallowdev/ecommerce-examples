from django.http import HttpResponse
from django.template import loader
from django.urls import path, include

from cosmos.views import index_cosmos


def checkout_cosmos(request):
    context = {'segment': 'index'}

    html_template = loader.get_template('cosmos/checkout/checkout.html')
    return HttpResponse(html_template.render(context, request))


def cart_cosmos(request):
    context = {'segment': 'index'}

    html_template = loader.get_template('cosmos/checkout/cart.html')
    return HttpResponse(html_template.render(context, request))


urlpatterns = [
    path('', index_cosmos, name='index_cosmos'),
    path('checkout/', checkout_cosmos, name='checkout_cosmos'),
    path('users/', include('users.urls')),
    path('stocks/', include('stocks.urls')),
]
