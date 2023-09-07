from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.shortcuts import HttpResponse, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)
from api.filters import RecipeFilter
from api.permissions import AuthorOrReadOnly
from api.serializers import (
    FavoriteSerializer,
    FollowGetSerializer,
    FollowSerializer,
    IngredientSerializer,
    RecipeCreateSerializer,
    RecipeCutSerializer,
    RecipeGetSerializer,
    ShoppingCartSerializer,
    TagSerializer,
    UserGetSerializer,
)

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    """Джосер вьюсет для работы с пользователями."""

    queryset = User.objects.all()
    serializer_class = UserGetSerializer
    permission_classes = [AuthorOrReadOnly]

    @action(
        detail=True,
        methods=["POST", "DELETE"],
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, id):
        """Подписка и отписка от авторов."""
        user = request.user
        author = get_object_or_404(User, id=id)
        if request.method == "POST":
            serializer = FollowSerializer(
                data={"user": user.id, "author": author.id},
                context={"request": request},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == "DELETE":
            serializer = FollowSerializer(
                data={"user": request.user.id, "author": author.id},
                context={"request": request},
            )
            if serializer.is_valid:
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {"errors": "Вы не подписаны на автора"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(
        detail=False,
        permission_classes=[IsAuthenticated],
    )
    def subscriptions(self, request):
        """Отображение подписок пользователя."""
        queryset = User.objects.filter(following__user=request.user)
        pages = self.paginate_queryset(queryset)
        serializer = FollowGetSerializer(
            pages, many=True, context={"request": request}
        )
        return self.get_paginated_response(serializer.data)


class TagViewSet(ModelViewSet):
    """Вьюсет для  работы с тегами."""

    permission_classes = [AuthorOrReadOnly]
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    permission_classes = [AuthorOrReadOnly]
    """Вьюсет для работы с ингредиентами."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    """Вьюсет для работы с рецептами."""

    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    permission_classes = [AuthorOrReadOnly]

    def get_queryset(self):
        return Recipe.objects.prefetch_related(
            "recipeingredients__ingredient", "tags"
        ).all()

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return RecipeGetSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def post_model(self, pk, serializer):
        """Добавление экземпляров модели Favorite/Shopping_cart."""
        recipe = get_object_or_404(Recipe, id=pk)
        serializer = serializer(
            data={
                "user": self.request.user.id,
                "recipe": recipe.id,
            },
            context={"request": self.request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        get_serializer = RecipeCutSerializer(recipe)
        return Response(
            get_serializer.data, status=status.HTTP_201_CREATED
        )
        
    def delete_model(self, model, pk, serializer):
        """Удаление экземпляров модели Favorite/Shopping_cart."""
        recipe = get_object_or_404(Recipe, id=pk)
        serializer = serializer(
            data={
                "user": self.request.user.id,
                "recipe": recipe.id,
            },
            context={"request": self.request},
        )
        if not model.objects.filter(
            user=self.request.user, recipe=recipe
        ).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        model.objects.filter(user=self.request.user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(
        detail=True,
        methods=["POST", "DELETE"],
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, pk):
        """Метод для работы с избранными рецептами."""
        return self.post_or_del(Favorite, pk, FavoriteSerializer)

    @action(
        detail=True,
        methods=["POST", "DELETE"],
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request, pk):
        """Метод для работы с корзиной."""
        return self.post_or_del(ShoppingCart, pk, ShoppingCartSerializer)

    def create_shopping_cart(self, ingredients):
        shopping_cart = ["Список необходимых ингредиентов:"]
        for ingredient in ingredients:
            name = ingredient["ingredient__name"]
            measurement_unit = ingredient["ingredient__measurement_unit"]
            amount = ingredient["ingredient_sum"]
            shopping_cart.append(f"\n{name} - {amount} {measurement_unit}")
        response = HttpResponse(shopping_cart, content_type="text/plain")
        response["Content-Disposition"] = "attachment;"
        return response

    @action(
        detail=False,
        methods=["GET"],
        permission_classes=[IsAuthenticated],
    )
    def download_shopping_cart(self, request):
        """Отправка пользователю txt файла с необходимыми ингредиентами."""
        ingredients = (
            RecipeIngredient.objects.filter(recipe__cart__user=request.user)
            .values("ingredient__name", "ingredient__measurement_unit")
            .order_by("ingredient__name")
            .annotate(ingredient_sum=Sum("amount"))
        )
        return self.create_shopping_cart(ingredients)
