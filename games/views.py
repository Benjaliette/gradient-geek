import pandas as pd

from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from games.helpers import get_recommendations, recommend_by_category

from games.models import Game

PLATFORMS = ['PC', 'PS4', 'NS', 'WIIU', '3DS', 'XONE', 'XBOX', 'PS3', 'X360',
            'SAT', 'GBA', 'VITA', 'WII', 'GC', 'N64', 'NGE', 'PS', 'SNES',
            'DC', 'PS2', 'DS', 'MOBI', 'PSP', 'BB', 'IOS', 'NES', 'GEN', 'ZOD',
            'NGPC', 'GBC']

CATEGORIES = ["Action", "Sport", "Music", "Shooter", "Adventure", "Arcade",
              "Visual Novel", "Card Board Game", "Tactical", "Point and Click",
              "MOBA", "Real Time Strategy", "Quiz/Trivia", "Pinball", "RPG",
              "Brawler", "Indie", "Turn Based Strategy", "Racing", "Platform",
              "Simulator", "Fighting", "Strategy", "Puzzle"]

class GameList(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'game_list.html'

    def get(self, request):
        category = request.query_params.get('category', None)

        if category != None:
            queryset = Game.objects.filter(genre__contains = category)
        else:
            queryset = None

        return Response({
            'games': queryset,
            'reco_games': None,
            "platforms": PLATFORMS,
            "categories": CATEGORIES
        })

    def post(self, request):
        game1 = request.data["game-1"]
        game2 = request.data["game-2"]
        game3 = request.data["game-3"]
        game4 = request.data["game-4"]
        platform = request.data["platform"]
        like = request.data["like"]
        category = request.query_params.get('category', None)

        if category != None:
            cat_queryset = Game.objects.filter(genre__contains = category)
        else:
            cat_queryset = Game.objects.all()

        user_games = []
        for game in [game1, game2, game3, game4]:
            if game != "" : user_games.append(game.strip())

        df = pd.DataFrame.from_records(Game.objects.all().values())

        recommendations = get_recommendations(user_games, platform, df, like != "true")

        try:
            if len(recommendations["name"].tolist()) != 0:
                queryset = Game.objects.none()
                for index, column in recommendations.iterrows():
                    print(column["overall_mean_score"])
                    retrievedGame = Game.objects.filter(name=column["name"], platform=platform)
                    retrievedGame.update(overall_mean_score=column["overall_mean_score"])
                    queryset |= retrievedGame
        except:
            queryset = None

        return Response({
            'games': cat_queryset,
            'reco_games': queryset,
            "platforms": PLATFORMS,
            "categories": CATEGORIES
        })
