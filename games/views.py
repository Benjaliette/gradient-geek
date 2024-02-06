from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from games.helpers import recommend_by_category

from games.models import Game

class GameList(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'game_list.html'

    def get(self, request):
        category = request.query_params.get('category', None)

        if category != None:
            queryset = Game.objects.filter(genre__contains = "RPG")
        else:
            queryset = Game.objects.all()

        print(queryset.count())

        return Response({'games': queryset})
