from django.contrib import messages
from django.shortcuts import render, redirect

from ..models import Brands, Category, Product, Unity


def product_list_home(request):
    try:
        products = Product.objects.exclude(status__in=['CANCEL', 'ARCHIVE', 'DISABLE']).order_by('-pk')

        categories = Category.objects.exclude(status='ARCHIVE').order_by('-pk')
        brands = Brands.objects.exclude(status='ARCHIVE').order_by('-pk')
        unities = Unity.objects.exclude(status='ARCHIVE').order_by('-pk')

        return render(request, 'cosmos/stocks/products/product_list.html',
                      {"unities": unities, "brands": brands, "categories": categories, "products": products})
    except Exception as ex:
        print(f'## EXCEPTION: {ex}')
        messages.error(request, 'Erreur de traitement du serveur..')
        return redirect('unities')


def product_by_category_list_home(request, category_id=None):
    try:
        if category_id is None:
            products = Product.objects.exclude(status__in=['CANCEL', 'ARCHIVE', 'DISABLE']).filter(category_id=category_id).order_by('-pk')
        else:
            products = Product.objects.exclude(status__in=['CANCEL', 'ARCHIVE', 'DISABLE']).order_by('-pk')
        categories = Category.objects.exclude(status='ARCHIVE').order_by('-pk')
        brands = Brands.objects.exclude(status='ARCHIVE').order_by('-pk')
        unities = Unity.objects.exclude(status='ARCHIVE').order_by('-pk')

        return render(request, 'cosmos/stocks/products/product_list.html',
                      {"unities": unities, "brands": brands, "categories": categories, "products": products})
    except Exception as ex:
        print(f'## EXCEPTION: {ex}')
        messages.error(request, 'Erreur de traitement du serveur..')
        return redirect('unities')


def category_list_home(request):
    try:
        categories = Category.objects.exclude(status__in=['CANCEL', 'ARCHIVE', 'DISABLE']).order_by('-pk')
        return render(request, 'cosmos/stocks/products/product_list.html',
                      {"categories": categories})
    except Exception as ex:
        print(f'## EXCEPTION: {ex}')
        messages.error(request, 'Erreur de traitement du serveur..')
        return redirect('unities')
