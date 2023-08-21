from django.shortcuts import render, HttpResponse
from djoser.views import UserViewSet

# Create your views here.
def index(request):
    return HttpResponse('index')

class CustomUserViewSet(UserViewSet):
    pass
