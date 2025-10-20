from django.urls import path

from . import unity_views as views

urlpatterns = [
    path('', views.UnityListView.as_view(), name='unities'),
]
