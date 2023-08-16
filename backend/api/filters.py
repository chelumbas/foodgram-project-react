from django_filters.filters import ModelMultipleChoiceFilter, CharFilter
from django_filters.rest_framework.filterset import FilterSet, BooleanFilter

from .models import Tag, Ingredient, Recipe


class RecipeFilter(FilterSet):
    tags = ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    is_favorited = BooleanFilter(
        method='get_is_favorited'
    )
    is_in_shopping_cart = BooleanFilter(
        method='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author')

    def get_is_favorited(self, queryset, field_name, value):
        user = self.request.user
        if user.is_authenticated and value:
            return queryset.filter(favorited_by__user=user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, field_name, value):
        user = self.request.user
        if user.is_authenticated and value:
            return queryset.filter(in_shopping_cart__user=user)
        return queryset


class IngredienFilter(FilterSet):
    name = CharFilter(lookup_expr='startswith')

    class Meta:
        model = Ingredient
        fields = ('name',)
