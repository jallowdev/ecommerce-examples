from django.contrib import admin
from django.contrib.admin import ModelAdmin

from users.models import User, Entity, AuthSession


@admin.register(User)
class CustomAdmin(ModelAdmin):
    list_display = ('id','identity', 'email', 'first_name', 'last_name', 'phone', 'entity__title', 'address__country','last_login', 'status')
    list_filter = ('first_name', 'last_name')


@admin.register(Entity)
class EntityAdmin(ModelAdmin):
    list_display = ('id', 'identity', 'title', 'subtitle', 'entitytype', 'status')
    list_filter = ('status', 'entitytype')

'''
@admin.register(AuthSession)
class SessionAdmin(ModelAdmin):
    list_display = ('id', 'identity', 'account', 'token', 'refresh', 'status')
    list_filter = ('status', 'account')

'''
