import base64

from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from users.models import Follow, User
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]

            data = ContentFile(base64.b64decode(imgstr), name="temp." + ext)

        return super().to_internal_value(data)


class UserGetSerializer(UserSerializer):
    """Гет сериализатор для работы с пользователями ."""

    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        )

    def get_is_subscribed(self, author):
        """Проверка на наличие подписки."""
        request = self.context.get("request")
        return (
            request
            and request.user.is_authenticated
            and request.user.follower.filter(author=author).exists()
        )


class UserSignupSerializer(UserCreateSerializer):
    """Создание пользователей."""

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "password",
        )


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор для пост подписок."""

    class Meta:
        model = Follow
        fields = "__all__"
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=("user", "author"),
                message="Уже подписаны на автора"
            )
        ]

    def validate(self, data):
        request = self.context.get("request")
        if request.user == data.get("author"):
            raise serializers.ValidationError(
                "Нельзя подписаться на себя"
            )
        return data

    def to_representation(self, instance):
        request = self.context.get("request")
        return FollowGetSerializer(
            instance.author, context={"request": request}
        ).data


class RecipeCutSerializer(serializers.ModelSerializer):
    """Сериализатор для краткой информации по рецепту"""

    class Meta:
        model = Recipe
        fields = ("id", "name", "cooking_time", "image")


class FollowGetSerializer(UserGetSerializer):
    """Сериализатор для гет подписок."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        request = self.context.get("request")
        recipes_limit = None
        if request:
            recipes_limit = request.query_params.get("recipes_limit")
        recipes = obj.recipes.all()
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
            serializer = RecipeCutSerializer(
                recipes, many=True, read_only=True
            )
            return serializer.data


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с тегами."""

    class Meta:
        model = Tag
        fields = "__all__"


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с ингредиентами."""

    class Meta:
        model = Ingredient
        fields = "__all__"


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Гет сериализатор для ингредиентов в рецептах."""

    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.CharField(source="ingredient.name")
    measurement_unit = serializers.CharField(
        source="ingredient.measurement_unit"
    )

    class Meta:
        model = RecipeIngredient
        fields = ("id", "name", "measurement_unit", "amount")


class RecipeGetSerializer(serializers.ModelSerializer):
    """Гет сериализатор для работы с рецептами."""

    author = UserGetSerializer(read_only=True)
    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientSerializer(
        many=True, read_only=True, source="recipeingredients"
    )
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    def get_is_favorited(self, obj):
        user = self.context.get("request").user
        if user.is_authenticated:
            return user.favorite.filter(recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get("request").user
        if user.is_authenticated:
            return user.cart.filter(recipe=obj).exists()
        return False

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "ingredients",
            "author",
            "name",
            "is_favorited",
            "is_in_shopping_cart",
            "image",
            "text",
            "cooking_time",
        )


class RecipeIngredientsCreateSerializer(serializers.ModelSerializer):
    """Пост сериализатор для ингредиентов."""

    id = serializers.IntegerField(write_only=True)

    class Meta:
        model = RecipeIngredient
        fields = ("id", "amount")


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор создания/редактирования рецепта."""

    ingredients = RecipeIngredientsCreateSerializer(
        many=True,
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            "name",
            "cooking_time",
            "text",
            "tags",
            "ingredients",
            "image",
        )

    def create_ingredients(
        self,
        ingredients,
        instance,
    ):
        RecipeIngredient.objects.bulk_create(
            [
                RecipeIngredient(
                    ingredient=get_object_or_404(
                        Ingredient, id=ingredient_data["id"]
                    ),
                    recipe=instance,
                    amount=ingredient_data["amount"],
                )
                for ingredient_data in ingredients
            ]
        )
    
    def validate(self, data):
        inrgedients_ids = [ing["id"] for ing in data.get("ingredients")]
        unique_inrgedients_ids = set(inrgedients_ids)
        if len(unique_inrgedients_ids) != len(inrgedients_ids):
            raise serializers.ValidationError(
                "Ингредиенты повторяются"
            )
        return data

    def create(self, validated_data):
        ingredients = validated_data.pop("ingredients")
        instance = super().create(validated_data)
        self.create_ingredients(ingredients, instance)
        return instance

    def update(self, instance, validated_data):
        ingredients = validated_data.pop("ingredients")
        instance.ingredients.clear()
        super().update(instance, validated_data)
        self.create_ingredients(ingredients, instance)
        instance.save()
        return instance

    def to_representation(self, instance):
        request = self.context.get("request")
        context = {"request": request}
        return RecipeGetSerializer(instance, context=context).data


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с избранным."""

    class Meta:
        model = Favorite
        fields = "__all__"


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с корзиной покупок."""

    class Meta:
        model = ShoppingCart
        fields = "__all__"
