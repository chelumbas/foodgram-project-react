from django.conf import settings
from django.contrib import admin

from .models import Favorite, Ingredient, Recipe, ShoppingCart, Tag

admin.site.empty_value_display = settings.DEFAULT_ADMIN_EMPTY_VALUE


@admin.register(Tag)
class TagsAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'color', 'slug')
    list_filter = ('name', 'slug')
    search_fields = ('name', 'slug')


@admin.register(Ingredient)
class IngredientsAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)


@admin.register(Recipe)
class RecipesAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'author',
        'name',
        'image',
        'text',
        'cooking_time',
        'publication_date'
    )
    list_filter = ('author', 'name', 'tags')
    search_fields = ('author', 'name', 'tags')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')
    search_fields = ('user',)


@admin.register(Favorite)
class FavoritesAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')
    search_fields = ('user',)
