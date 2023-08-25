import base64

from djoser.serializers import UserCreateSerializer, UserSerializer
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from recipes.models import Tag, Recipe, RecipeIngredient, Ingredient, Favorite, Shopping_cart
from django.core.files.base import ContentFile
from users.models import User, Follow

class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class UserGetSerializer(UserSerializer):
    """"""

    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'username',
                  'first_name', 'last_name', 'is_subscribed',)

    def get_is_subscribed(self, author):
        """."""
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and request.user.follower.filter(author=author).exists())
    
class UserSignupSerializer(UserCreateSerializer):
    """."""
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'password')



class TagSerializer(serializers.ModelSerializer):
    """."""

    class Meta:
        model = Tag
        fields = '__all__'

class IngredientSerializer(serializers.ModelSerializer):
    """."""

    class Meta:
        model = Ingredient
        fields = '__all__'

class RecipeIngredientSerializer(serializers.ModelSerializer):
    """."""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(source='ingredient.measurement_unit')
    
    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeGetSerializer(serializers.ModelSerializer):
    """."""
    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientSerializer(many=True, 
                                             read_only=True, 
                                             source='recipeingredients')
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    
    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.favorite.filter(recipe=obj).exists()
    
    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.cart.filter(recipe=obj).exists()
    
    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'ingredients', 'author', 'name',
                  'is_favorited', 'is_in_shopping_cart', 
                  'image', 'text', 'cooking_time')


class RecipeIngredientsCreateSerializer(serializers.ModelSerializer):
    """."""
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all()
    )
    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeCreateSerializer(serializers.ModelSerializer):
    """."""
    ingredients = RecipeIngredientsCreateSerializer(many=True,)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                            many=True)
    class Meta:
        model = Recipe
        fields = ('name', 'cooking_time', 'text', 'tags', 'ingredients')

    def create_ingredients(self, ingredients, recipe):
        RecipeIngredient.objects.bulk_create(
            [RecipeIngredient(
                ingredient=get_object_or_404(Ingredient, id=ingredient['id']),
                recipe=recipe,
                amount=ingredient.get('amount')
            ) for ingredient in ingredients]
        )

    def create(self, validated_data):
        request = self.context.get('request')
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        print(request.user.id)
        print(**validated_data)
        recipe = Recipe.objects.create(author=request.user.id, **validated_data)
        self.create_ingredients(ingredients, recipe)
        return recipe
    

class FavoriteSerializer(serializers.ModelSerializer):
    """."""
    class Meta:
        model = Favorite
        fields = '__all__'


class ShoppingCartSerializer(serializers.ModelSerializer):
    """."""
    class Meta:
        model = Shopping_cart
        fields = '__all__'