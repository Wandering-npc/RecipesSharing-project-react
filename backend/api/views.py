from django.shortcuts import render, HttpResponse
from djoser.views import UserViewSet
from rest_framework.viewsets import ModelViewSet
from api.serializers import TagSerializer, RecipeGetSerializer, RecipeCreateSerializer


from recipes.models import Tag, Recipe
# Create your views here.
def index(request):
    return HttpResponse('index')

class CustomUserViewSet(UserViewSet):
    pass

class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeGetSerializer

    def get_queryset(self):
        recipes = Recipe.objects.prefetch_related('recipeingredients__ingredient',
                                                   'tags'
                                                  ).all()
        return recipes
    
    def get_serializer_class(self):
        if self.action == 'create':
            return RecipeCreateSerializer
        return RecipeGetSerializer
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
        return super().perform_create(serializer)