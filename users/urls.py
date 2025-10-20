from django.urls import path

from users.views import LoginView, logout_view, register_user

urlpatterns = [
    path('login/', LoginView.as_view(), name='login_cosmos'),
    path('logout/', logout_view, name='logout_cosmos'),
    path('register/', register_user, name='register_cosmos'),
]
