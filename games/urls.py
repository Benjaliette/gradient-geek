from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GameList

router = DefaultRouter()

urlpatterns = [
    path('', GameList.as_view(), name='game_list')
]
