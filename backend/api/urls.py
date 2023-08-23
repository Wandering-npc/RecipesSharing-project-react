from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import index, CustomUserViewSet, TagViewSet, RecipeViewSet

router = DefaultRouter()
router.register('users', CustomUserViewSet)
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'tags', TagViewSet, basename='tags')
#router.register(r'ingredients', IngredientsViewSet, basename='ingredients')

urlpatterns = [
    path('index', index),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls))
]
