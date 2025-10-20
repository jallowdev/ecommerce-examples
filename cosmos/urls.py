from django.http import HttpResponse
from django.template import loader
from django.urls import path, include


def index_cosmos(request):
    context = {'segment': 'index'}

    html_template = loader.get_template('cosmos/home/home3.html')
    return HttpResponse(html_template.render(context, request))


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

]
