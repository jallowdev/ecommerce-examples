
from django.contrib import admin
from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader
from django.urls import path


def index(request):
    context = {'segment': 'index'}

    html_template = loader.get_template('ecom/home/home.html')
    return HttpResponse(html_template.render(context, request))


urlpatterns = [
    #path('admin/', admin.site.urls),
    path('', index, name='home'),
]
