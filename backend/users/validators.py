from django.core.exceptions import ValidationError
from django.contrib.auth.validators import UnicodeUsernameValidator


def validate_username(value):
    if value == 'me':
        raise ValidationError(
            'Имя пользователя не может быть <me>.',
        )
    validator = UnicodeUsernameValidator()
    validator(value)
