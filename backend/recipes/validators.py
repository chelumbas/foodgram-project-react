import re

from django.core.exceptions import ValidationError


def validate_slug(slug: str) -> str:
    if ''.join(set(re.sub(r'^[-a-zA-Z0-9_]+$', '', slug))):
        raise ValidationError(
            'В слаге допустимы только буквы и цифры'
        )
    return slug


def validate_recipe_min_time(time):
    if time >= 1:
        return time
    raise ValidationError(
        'Время обязательно больше 1 минуты.'
    )


def validate_ingredient_amount(ingredient):
    if ingredient > 1:
        return ingredient
    raise ValidationError(
        'Для рецепта необходим хотя бы один ингредиент'
    )
