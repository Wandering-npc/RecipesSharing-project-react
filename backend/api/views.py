from django.shortcuts import HttpResponse
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.db.models import Sum
from djoser.views import UserViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from api.serializers import (TagSerializer, RecipeGetSerializer, 
                             RecipeCreateSerializer, IngredientSerializer, 
                             UserGetSerializer, FollowSerializer, RecipeCutSerializer,
                             FavoriteSerializer, ShoppingCartSerializer, FollowGetSerializer)
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from api.filters import RecipeFilter
from api.permissions import AuthorAdminOrReadOnly

User = get_user_model()

from recipes.models import (Tag, Recipe, Ingredient,
                            Shopping_cart, Favorite, RecipeIngredient)
from users.models import Follow


class CustomUserViewSet(UserViewSet):
    """Джосер вьюсет для работы с пользователями."""
    queryset = User.objects.all()
    serializer_class = UserGetSerializer
    permission_classes = [AuthorAdminOrReadOnly]

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated],)
    def subscribe(self, request, id):
        """Подписка и отписка от авторов."""
        user = request.user
        author = get_object_or_404(User, id=id)
        if request.method == 'POST':
            serializer = FollowSerializer(
                data={'user': request.user.id, 'author': author.id},
                context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
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
        permission_classes=[AuthorAdminOrReadOnly],
    )
    def subscriptions(self, request):
        """Отображение подписок пользователя."""
        queryset = User.objects.filter(following__user=request.user)
        pages = self.paginate_queryset(queryset)
        serializer = FollowGetSerializer(pages,
                                      many=True,
                                      context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


#class FavoriteViewSet(ModelViewSet):
    #serializer_class = FavoriteSerializer

    #def get_queryset(self):
        #print('0')
        #recipe_id = self.kwargs.get('recipe_id')
        #print('2')
        #recipe = get_object_or_404(Recipe, id=recipe_id)
        #return recipe.favorite.all()   


class TagViewSet(ModelViewSet):
    """Вьюсет для  работы с тегами."""
    permission_classes = [AuthorAdminOrReadOnly]
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None

class IngredientViewSet(ReadOnlyModelViewSet):
    permission_classes = [AuthorAdminOrReadOnly]
    """Вьюсет для работы с ингредиентами."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    """Вьюсет для работы с рецептами."""
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    permission_classes = [AuthorAdminOrReadOnly]
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
        """Добавление и удаление экземпляров модели Favorite/Shopping_Cart."""
        recipe = get_object_or_404(Recipe, id=pk)
        serializer = serializer(
            data={'user': self.request.user.id, 'recipe': recipe.id, },
            context={'request': self.request}
        )
        if self.request.method == 'POST':
            serializer.is_valid(raise_exception=True)
            serializer.save()
            get_serializer = RecipeCutSerializer(recipe)
            return Response(get_serializer.data, status=status.HTTP_201_CREATED)
        if not model.objects.filter(user=self.request.user,
                                     recipe=recipe).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        model.objects.filter(user=self.request.user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        """Метод для работы с избранными рецептами."""
        return self.post_or_del(Favorite, pk, FavoriteSerializer)
        
    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        """Метод для работы с корзиной."""
        return self.post_or_del(Shopping_cart, pk, ShoppingCartSerializer)
    
    @action(detail=False, 
            url_path='download_shopping_cart',
            url_name='download_shopping_cart')
    def download_shopping_cart(self, request):
        """Отправка пользователю txt файла с необходимыми ингредиентами."""
        ingredients = RecipeIngredient.objects.filter(
        recipe__cart__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).order_by(
            'ingredient__name'
        ).annotate(ingredient_total=Sum('amount'))
        shopping_cart = ['Список необходимых ингредиентов:']
        for ingredient in ingredients:
            name = ingredient['ingredient__name']
            measurement_unit = ingredient['ingredient__measurement_unit']
            amount = ingredient['ingredient_total']
            shopping_cart.append(
                f'\n{name} - {amount} {measurement_unit}')
        response = HttpResponse(shopping_cart, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="test.txt"'
        return response
