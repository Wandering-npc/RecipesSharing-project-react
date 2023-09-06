from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

from users.validators import validate_username


MAX_LENGTH_FOR_ANY_NAME = 25
MAX_LENGTH_FOR_EMAIL = 254
MAX_LENGTH_FOR_PASSWORD = 150


class User(AbstractUser):
    email = models.EmailField(
        max_length=MAX_LENGTH_FOR_EMAIL,
        verbose_name="Эл. почта",
        unique=True,
    )
    username = models.CharField(
        validators=(validate_username, UnicodeUsernameValidator),
        max_length=MAX_LENGTH_FOR_ANY_NAME,
        verbose_name="Имя пользователя",
        unique=True,
    )
    password = models.CharField(
        "Пароль",
        max_length=MAX_LENGTH_FOR_PASSWORD,
    )
    first_name = models.CharField(
        verbose_name="Имя",
        max_length=MAX_LENGTH_FOR_ANY_NAME,
    )
    last_name = models.CharField(
        verbose_name="Фамилия",
        max_length=MAX_LENGTH_FOR_ANY_NAME,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "username",
        "first_name",
        "last_name",
    ]

    class Meta:
        ordering = ("id",)
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

        constraints = [
            models.CheckConstraint(
                check=~models.Q(username__iexact="me"),
                name="username_is_not_me",
            )
        ]


class Follow(models.Model):
    """Модель подписки."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower",
        verbose_name="Подписчик",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following",
        verbose_name="Автор",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "author"],
                name="unique_follow",
            ),
            models.CheckConstraint(
                check=~models.Q(author=models.F("user")),
                name="user_is_not_author"
            ),
        ]
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"

    def __str__(self):
        return(
            f"Пользователь {self.user.username}"
            f"подписан на {self.author.username}"
        )
