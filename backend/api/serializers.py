import base64

from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer, UserSerializer
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from rest_framework.serializers import (CharField, ImageField, IntegerField,
                                        ModelSerializer,
                                        PrimaryKeyRelatedField,
                                        SerializerMethodField)
from rest_framework.validators import UniqueTogetherValidator
from users.models import Subscription, User


class DefaultUserSerializer(UserSerializer):
    is_subscribed = SerializerMethodField(
        read_only=True,
        method_name='get_is_subscribed'
    )

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, author):
        user = self.context.get('request').user
        return (
            user.is_authenticated and user.subscriptions.filter(
                author=author
            ).exists()
        )


class DefaultUserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password')


class SubscriptionSerializer(DefaultUserSerializer):

    recipes_count = SerializerMethodField(
        read_only=True,
        method_name='get_recipes_count'
    )
    recipes = SerializerMethodField(
        read_only=True,
        method_name='get_recipes'
    )

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_recipes_count(self, an_object):
        return an_object.recipes.count()

    def get_recipes(self, an_object):
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')
        recipes = an_object.recipes.all()
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        return RecipeShortSerializer(
            recipes,
            many=True,
            context={'request': request}
        ).data


class SubscribeSerializer(ModelSerializer):
    class Meta:
        model = Subscription
        fields = ('id', 'user', 'author')

        validators = (
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('user', 'author')
            ),
        )


class TagsSerializer(ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientsSerializer(ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class FavoriteSerializer(ModelSerializer):
    class Meta:
        model = Favorite
        fields = '__all__'

        validators = (
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт был добавлен в избранное'
            ),
        )


class ShoppingCartSerializer(ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = '__all__'

        validators = (
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт был добавлен в список покупок'
            ),
        )


class RecipeShortSerializer(ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'cooking_time', 'image')


class Base64ImageField(ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class DefaultIngredientAmountSerializer(ModelSerializer):
    id = IntegerField(source='ingredient.id', read_only=True)
    name = CharField(source='ingredient.name', read_only=True)
    measurement_unit = CharField(
        source='ingredient.measurement_unit',
        read_only=True
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class DefaultRecipeSerializer(ModelSerializer):
    tags = TagsSerializer(many=True)
    author = DefaultUserSerializer()
    ingredients = DefaultIngredientAmountSerializer(
        many=True,
        source='ingredient'
    )
    is_favorited = SerializerMethodField(
        method_name='get_is_favorited'
    )
    is_in_shopping_cart = SerializerMethodField(
        method_name='get_is_in_shopping_cart'
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def _is_auth_and_exists_in_model(self, model, an_object):
        user = self.context.get('request').user
        return user.is_authenticated and model.objects.filter(
            user=user,
            recipe=an_object
        ).exists()

    def get_is_favorited(self, an_object):
        return self._is_auth_and_exists_in_model(Favorite, an_object)

    def get_is_in_shopping_cart(self, an_object):
        return self._is_auth_and_exists_in_model(ShoppingCart, an_object)


class IngredientAmountWriteSerializer(ModelSerializer):
    id = IntegerField()
    amount = IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeWriteSerializer(ModelSerializer):
    ingredients = IngredientAmountWriteSerializer(
        many=True,
        source='ingredient'
    )
    tags = PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time'
        )

    def do_ingredients_and_tags(self, recipe, ingredients, tags):
        RecipeIngredient.objects.bulk_create(
            [
                RecipeIngredient(
                    recipe=recipe,
                    ingredient=Ingredient.objects.get(
                        id=ingredient.get('id')
                    ),
                    amount=ingredient.get('amount')
                ) for ingredient in ingredients
            ]
        )
        recipe.tags.set(tags)

    def create(self, input_data):
        ingredients = input_data.pop('ingredient')
        tags = input_data.pop('tags')
        recipe = Recipe.objects.create(
            author=self.context.get('request').user,
            **input_data
        )
        self.do_ingredients_and_tags(recipe, ingredients, tags)
        return recipe

    def update(self, recipe, input_data):
        ingredients = input_data.pop('ingredient')
        tags = input_data.pop('tags')
        recipe.ingredients.clear()
        recipe.tags.clear()
        self.do_ingredients_and_tags(recipe, ingredients, tags)
        return super().update(recipe, input_data)

    def represent(self, recipe):
        return DefaultRecipeSerializer(
            recipe,
            context={'request': self.context['request']}
        ).data
