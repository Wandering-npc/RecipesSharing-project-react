from django.contrib.auth.models import AbstractUser
from django.db import models

from users.validators import validate_username


class User(AbstractUser):
    email = models.EmailField(
        max_length=254,
        verbose_name="Эл. почта",
        unique=True,
    )
    username = models.CharField(
        validators=(validate_username,),
        max_length=150,
        verbose_name="Имя пользователя",
        unique=True,
    )
    password = models.CharField(
        "Пароль",
        max_length=150,
    )
    first_name = models.CharField(
        verbose_name="Имя",
        max_length=25,
    )
    last_name = models.CharField(
        verbose_name="Фамилия",
        max_length=25,
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
