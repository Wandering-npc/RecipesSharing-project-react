from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import index, CustomUserViewSet, TagViewSet, RecipeViewSet, IngredientViewSet

router = DefaultRouter()
router.register(r'users', CustomUserViewSet)
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = [
    path('index', index),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    
]
