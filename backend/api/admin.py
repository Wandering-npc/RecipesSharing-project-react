from django.contrib import admin

from recipes.models import Tag, Recipe, Ingredient, RecipeIngredient
from users.models import Follow
class RecipeIngredientInLine(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (RecipeIngredientInLine,)
    pass


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    pass

@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    pass