from dataclasses import dataclass


@dataclass
class Attachment:
    name: str
    body: str


def generate_attachment(user_name, recipes, ingredients) -> Attachment:
    file_name = str(user_name) + '_ingredients.txt'
    topic = 'Список покупок для приготовления:\n'
    body = topic + ', '.join(recipe.name for recipe in recipes)
    for ingredient in ingredients:
        name = ingredient.get('ingredient__name')
        amount = ingredient.get('ingredient_amount')
        measurement = ingredient.get('ingredient__measurement_unit')
        body += ''.join(f'\n{name}: {amount}, {measurement}')

    return Attachment(name=file_name, body=body)
