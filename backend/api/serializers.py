import base64

from rest_framework import serializers
from recipes.models import Tag, Recipe, RecipeIngredient, Ingredient, Favorite, Shopping_cart
from django.core.files.base import ContentFile

class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):
    """"""

    class Meta:
        model = Tag
        fields = '__all__'

class IngredientSerializer(serializers.ModelSerializer):
    """"""

    class Meta:
        model = Ingredient
        fields = '__all__'

class RecipeIngredientSerializer(serializers.ModelSerializer):
    """"""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(source='ingredient.measurement_unit')
    
    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeGetSerializer(serializers.ModelSerializer):
    """"""
    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientSerializer(many=True, 
                                             read_only=True, 
                                             source='recipeingredients')
    favorite = serializers.SerializerMethodField()
    shopping_cart = serializers.SerializerMethodField()
    
    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'ingredients', 'author', 'name',
                  'favorite', 'shopping_cart', 
                  'image', 'text', 'cooking_time')


class RecipeIngredientsCreateSerializer(serializers.ModelSerializer):
    """"""
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all()
    )
    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeCreateSerializer(serializers.ModelSerializer):
    """"""
    ingredients = RecipeIngredientsCreateSerializer(many=True,)

    class Meta:
        model = Recipe
        fields = ('name', 'cooking_time', 'text', 'tags', 'ingredients')

    def create(self, validated_data):
        print(validated_data)
        ingredients = validated_data.pop('ingredients')
        instance = super().create(validated_data)
        return instance
    

class FavoriteSerializer(serializers.ModelSerializer):
    """"""
    class Meta:
        model = Favorite
        fields = '__all__'


class ShoppingCartSerializer(serializers.ModelSerializer):
    """"""
    class Meta:
        model = Shopping_cart
        fields = '__all__'