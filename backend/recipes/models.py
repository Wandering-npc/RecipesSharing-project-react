from django.db import models


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=245,
        unique=True,
        blank=False,
        null=False
    )
    color = models.CharField(
        verbose_name='Цвет',
        max_length=7,
        unique=True,
        blank=False,
        null=False,
    )
    slug = models.SlugField(
        verbose_name='Slug',
        max_length=245,
        unique=True,
        blank=False,
        null=False, 
    )
    class Meta:
        verbose_name = 'Тег'
    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=100,
        blank=False,
        null=False,
    )
    amount = models.CharField(
        verbose_name='Количество',
        max_length=245,
        blank=False,
        null=False,
    )

    class Meta:
        verbose_name = 'Ингредиент'

    def __str__(self):
        return self.name
         