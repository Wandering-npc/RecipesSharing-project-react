from django.shortcuts import render, HttpResponse
from djoser.views import UserViewSet
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from api.serializers import (TagSerializer, RecipeGetSerializer, 
                             RecipeCreateSerializer, IngredientSerializer, 
                             UserGetSerializer, FollowSerializer, RecipeSmallSerializer,
                             FavoriteSerializer, ShoppingCartSerializer)
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status


User = get_user_model()

from recipes.models import Tag, Recipe, Ingredient, Shopping_cart, Favorite
from users.models import Follow

def index(request):
    return HttpResponse('index')

class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserGetSerializer

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated])
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)
        if request.method == 'POST':
            serializer = FollowSerializer(author,
                                            data=request.data,
                                            context={'request': request})
            serializer.is_valid(raise_exception=True)
            Follow.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            follow = Follow.objects.filter(user=user, author=author)
            if not follow.exists():
                return Response({'errors': 'Вы не подписаны на автора'},
                                status=status.HTTP_400_BAD_REQUEST)
            follow = get_object_or_404(Follow,
                                            user=user,
                                            author=author)
            follow.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
    @action(
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        queryset = User.objects.filter(following__user=request.user)
        pages = self.paginate_queryset(queryset)
        serializer = FollowSerializer(pages,
                                      many=True,
                                      context={'request': request}
        )
        return self.get_paginated_response(serializer.data)
    

class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

class IngredientViewSet(ReadOnlyModelViewSet):
    """."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()

    def get_queryset(self):
        recipes = Recipe.objects.prefetch_related('recipeingredients__ingredient',
                                                   'tags'
                                                  ).all()
        return recipes
    
    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeGetSerializer
        return RecipeCreateSerializer
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def post_or_del(self, model, pk, serializer):
        recipe = get_object_or_404(Recipe, id=pk)
        serializer = serializer(
            data={'user': self.request.user.id, 'recipe': recipe.id, },
            context={'request': self.request}
        )
        if self.request.method == 'POST':
            serializer.is_valid(raise_exception=True)
            serializer.save()
            serializer = RecipeSmallSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if not model.objects.filter(user=self.request.user,
                                     recipe=recipe).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        model.objects.filter(user=self.request.user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated, ]
    )
    def favorite(self, request, pk):
        """."""
        return self.post_or_del(Favorite, pk, FavoriteSerializer)
        

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated, ]
    )
    def shopping_cart(self, request, pk):
        """."""
        return (Shopping_cart, pk, ShoppingCartSerializer)

