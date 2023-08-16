from django.db.models import Sum
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework.permissions import (SAFE_METHODS, AllowAny,
                                        IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT
from rest_framework.viewsets import ModelViewSet
from users.models import Subscription, User

from .custom_functions import generate_attachment
from .filters import IngredienFilter, RecipeFilter
from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)
from .permissions import IsAuthorOrReadOnly
from .serializers import (DefaultRecipeSerializer, DefaultUserSerializer,
                          FavoriteSerializer, IngredientsSerializer,
                          RecipeWriteSerializer, ShoppingCartSerializer,
                          SubscribeSerializer, SubscriptionSerializer,
                          TagsSerializer)


class UsersViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = DefaultUserSerializer
    permission_classes = (AllowAny,)

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=(IsAuthenticatedOrReadOnly,)
    )
    def subscriptions(self, request):
        queryset = User.objects.filter(subscribers__user=request.user)
        page = self.paginate_queryset(queryset)
        serializer_data = SubscriptionSerializer(
            page,
            context={'request': request},
            many=True
        ).data
        return self.get_paginated_response(serializer_data)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)
        if request.method == 'POST':
            serializer_data = {'user': user.id, 'author': author.id}
            serializer = SubscribeSerializer(
                data=serializer_data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=HTTP_201_CREATED)
        model_object = get_object_or_404(
            Subscription,
            user=user,
            author=author
        )
        model_object.delete()
        return Response(status=HTTP_204_NO_CONTENT)


class RecipesViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return DefaultRecipeSerializer
        return RecipeWriteSerializer

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        url_path='shopping_cart',
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            serialized_data = {'user': user.id, 'recipe': recipe.pk}
            serializer = ShoppingCartSerializer(
                data=serialized_data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=HTTP_201_CREATED)
        model_object = get_object_or_404(
            ShoppingCart,
            user=user,
            recipe=recipe
        )
        model_object.delete()
        return Response(status=HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        user = request.user
        recipe = Recipe.objects.filter(in_shopping_cart__user=user)
        ingredients = RecipeIngredient.objects.filter(
            recipe__in=recipe
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(ingredient_amount=Sum('amount'))
        attachment = generate_attachment(user.username, recipe, ingredients)

        response = HttpResponse(attachment.body, content_type='text/plain')
        response['Content-Disposition'] = (
            f'attachment; filename={attachment.name}'
        )
        return response

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            serialized_data = {'user': user.id, 'recipe': recipe.id}
            serializer = FavoriteSerializer(
                data=serialized_data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=HTTP_201_CREATED)
        model_object = get_object_or_404(Favorite, user=user, recipe=recipe)
        model_object.delete()
        return Response(status=HTTP_204_NO_CONTENT)


class TagsViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagsSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientsViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientsSerializer
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredienFilter
    pagination_class = None
