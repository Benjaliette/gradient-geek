import pandas as pd

from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from games.helpers import get_recommendations, recommend_by_category

from games.models import Game

class GameList(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'game_list.html'

    def get(self, request):
        category = request.query_params.get('category', None)
        platforms = ['PC', 'PS4', 'NS', 'WIIU', '3DS', 'XONE', 'XBOX', 'PS3', 'X360',
            'SAT', 'GBA', 'VITA', 'WII', 'GC', 'N64', 'NGE', 'PS', 'SNES',
            'DC', 'PS2', 'DS', 'MOBI', 'PSP', 'BB', 'IOS', 'NES', 'GEN', 'ZOD',
            'NGPC', 'GBC']

        if category != None:
            queryset = Game.objects.filter(genre__contains = category)
        else:
            queryset = None

        return Response({'games': queryset, 'reco_games': None, "platforms": platforms})

    def post(self, request):
        game1 = request.data["game-1"]
        game2 = request.data["game-2"]
        platform = request.data["platform"]
        like = request.data["like"]
        category = request.query_params.get('category', None)

        if category != None:
            cat_queryset = Game.objects.filter(genre__contains = category)
        else:
            cat_queryset = Game.objects.all()

        platforms = ['PC', 'PS4', 'NS', 'WIIU', '3DS', 'XONE', 'XBOX', 'PS3', 'X360',
            'SAT', 'GBA', 'VITA', 'WII', 'GC', 'N64', 'NGE', 'PS', 'SNES',
            'DC', 'PS2', 'DS', 'MOBI', 'PSP', 'BB', 'IOS', 'NES', 'GEN', 'ZOD',
            'NGPC', 'GBC']

        user_games = [game.strip() for game in [game1, game2]]
        df = pd.DataFrame.from_records(Game.objects.all().values())

        recommendations = get_recommendations(user_games, platform, df, like != "true")

        try:
            if len(recommendations["name"].tolist()) != 0:
                queryset = Game.objects.filter(name__in=recommendations["name"].tolist())
        except:
            queryset = None

        return Response({'games': cat_queryset, 'reco_games': queryset, "platforms": platforms})
