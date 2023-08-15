from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import ()

router = DefaultRouter()

router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', IngredientsViewSet, basename='ingredients')
