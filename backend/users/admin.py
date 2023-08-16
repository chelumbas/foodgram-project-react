from django.conf import settings
from django.contrib import admin

from .models import Subscription, User

admin.site.empty_value_display = settings.DEFAULT_ADMIN_EMPTY_VALUE


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'username',
        'password',
        'email',
        'first_name',
        'last_name'
    )
    list_filter = ('username', 'email')
    search_fields = ('username', 'email')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'author')
    search_fields = ('user', 'author')
    list_filter = ('user', 'author')
