from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from users.models import User


class Tag(models.Model):
    name = models.CharField(
        verbose_name="Название",
        max_length=245,
        unique=True,
    )
    color = models.CharField(
        verbose_name="Цвет",
        max_length=7,
        unique=True,
    )
    slug = models.SlugField(
        verbose_name="Слаг",
        max_length=245,
        unique=True,
    )

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name="Название",
        max_length=100,
    )
    measurement_unit = models.CharField(
        verbose_name="е.и",
        max_length=245,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["name", "measurement_unit"],
                name="name_unit_ingredient"
            )
        ]
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name="Автор",
        on_delete=models.CASCADE,
        related_name="recipes",
    )
    name = models.CharField(
        verbose_name="Название",
        max_length=245,
    )
    image = models.ImageField(
        verbose_name="Картинка",
        upload_to="recipes/",
        blank=True,
    )
    text = models.TextField(verbose_name="Описание")
    ingredients = models.ManyToManyField(
        Ingredient,
        through="RecipeIngredient",
        through_fields=("recipe", "ingredient"),
        verbose_name="Ингредиенты",
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name="Теги",
    )
    cooking_time = models.PositiveSmallIntegerField(
        "Время приготовления",
        validators=[
            MinValueValidator(1, "Минимум 1 минута"),
            MaxValueValidator(60 * 24, "Максимум 24 часа"),
        ],
    )

    class Meta:
        ordering = ("-id",)
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="recipeingredients",
        verbose_name="Рецепт",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="recipeingredients",
        verbose_name="Ингредиент",
    )
    amount = models.PositiveSmallIntegerField(
        "Количество",
        validators=[
        MinValueValidator(1, "Минимум 1"),
        MaxValueValidator(999, "Максимум 999 единиц")]
    )

    class Meta:
        verbose_name = "Ингредиент в рецепте"
        verbose_name_plural = "Ингредиенты в рецепте"


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="favorite",
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="favorite",
        verbose_name="Рецепт",
    )

    class Meta:
        ordering = ("-id",)
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"], name="unique_user_recipe_favorite"
            )
        ]
        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="cart",
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="cart",
        verbose_name="Рецепт",
    )

    class Meta:
        ordering = ("-id",)
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"], name="unique_user_recipe_basket"
            )
        ]
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"
