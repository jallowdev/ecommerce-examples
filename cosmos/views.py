from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import loader

from stocks.models import Product, Category, Brands, Unity


# Create your views here.

def index_cosmos(request):
    try:
        products = Product.objects.exclude(status__in=['CANCEL', 'ARCHIVE', 'DISABLE']).order_by('-pk')

        categories = Category.objects.exclude(status='ARCHIVE').order_by('-pk')
        brands = Brands.objects.exclude(status='ARCHIVE').order_by('-pk')
        unities = Unity.objects.exclude(status='ARCHIVE').order_by('-pk')

        context = {"unities": unities, "brands": brands, "categories": categories, "products": products}

        print(f'## PRODUCT LENGH :{len(products)}')

        html_template = loader.get_template('cosmos/home/home3.html')
        return HttpResponse(html_template.render(context, request))

    except Exception as ex:
        print(f'## EXCEPTION: {ex}')
        messages.error(request, 'Erreur de traitement du serveur..')
        return redirect('index_cosmos')
