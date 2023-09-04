from django.contrib import admin

from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)


class RecipeIngredientInLine(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("pk", "name", "author", "favorite_count")
    inlines = (RecipeIngredientInLine,)
    list_filter = ("name", "author", "tags")

    def favorite_count(self, obj):
        return obj.favorite.count()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_filter = ("name",)


admin.site.register(Tag)
admin.site.register(Favorite)
admin.site.register(ShoppingCart)
