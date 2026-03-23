import traceback

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template import loader

from stocks.models import Product, Category, Brands, Unity


# Create your views here.

def index_cosmos(request):
    try:
        products = Product.objects.exclude(status__in=['CANCEL', 'ARCHIVE', 'DISABLE']).order_by('-pk')
        products_home = products.filter(is_home=True)
        products_trending = products.filter(is_trending=True)

        categories = Category.objects.exclude(status__in=['CANCEL', 'ARCHIVE', 'DISABLE']).order_by('-pk')
        brands = Brands.objects.exclude(status='ARCHIVE').order_by('-pk')
        unities = Unity.objects.exclude(status='ARCHIVE').order_by('-pk')

        product_parfums = categories.get(pk=1)
        product_parfums_eaux =  categories.get(pk=2)
        product_parfums_brume =  categories.get(pk=3)
        product_parfums_coffret =  categories.get(pk=4)

        product_maquillage =  categories.filter(pk=20).first()

        product_mode =  categories.filter(pk=30).first()

        product_corps =  categories.filter(pk=40).first()

        product_sacs =  categories.filter(pk=50).first()

        product_chaussures =  categories.filter(pk=60).first()



        context = {
            "unities": unities,
            "brands": brands,
            "categories": categories,
            "products": products,
            "products_home": products_home,
            "products_trending": products_trending,
            "product_parfums": product_parfums,
            "product_parfums_eaux": product_parfums_eaux,
            "product_parfums_brume": product_parfums_brume,
            "product_parfums_coffret": product_parfums_coffret,
        }

        print(f"## porducts: {products.count()} porduct_parfums: {product_parfums.get_products.count()} product_parfums_eaux :{product_parfums_eaux.get_products.count()}")

        html_template = loader.get_template('cosmos/home/home3.html')
        return HttpResponse(html_template.render(context, request))
        #return render(request, 'cosmos/home/home3.html', context=context)

    except Exception as ex:
        traceback.print_exc()
        print(f'## EXCEPTION: {ex}')
        messages.error(request, 'Erreur de traitement du serveur..')
        return redirect('index_cosmos')


def category_list(request, pk=None):
    try:
        if pk is not None:
            categories = Category.objects.filter(pk=pk).exclude(status__in=['CANCEL', 'ARCHIVE', 'DISABLE']).order_by(
                '-pk')
        else:
            categories = Category.objects.exclude(status__in=['CANCEL', 'ARCHIVE', 'DISABLE']).order_by('-pk')

        return render(request, 'cosmos/stocks/products/product_list.html',
                      {"categories": categories})
    except Exception as ex:
        print(f'## EXCEPTION: {ex}')
        messages.error(request, 'Erreur de traitement du serveur..')
        return redirect('unities')
