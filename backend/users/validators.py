import re

from django.core.exceptions import ValidationError


def validate_username(username: str) -> str:
    if username.lower() == 'me':
        raise ValidationError('Невалидный логин.')
    if ''.join(set(re.sub(r'^[\w.@+-]+$', '', username))):
        raise ValidationError('В логине допустимы только буквы и цифры')
    return username
