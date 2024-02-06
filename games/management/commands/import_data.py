from click import BaseCommand
from games.helpers import preprocessing_function
from games.models import Game
import pandas as pd

class Command(BaseCommand):
    help = "Seed data from CSV files"

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the CSV file')d

    def handle(self):
        try:
            if Game.objects.all().count() > 0:
                df = pd.read_csv('games/datasets/dataset_final.csv', delimiter=',', encoding='ISO-8859-1')
                df = preprocessing_function(df, ['Name', 'Platform'], 'Summary')
                for index, column in df.iterrows():
                    Game.objects.create(
                        name = column['Name'],
                        release_date = column['Release Date'],
                        number_of_reviews = column['Number of Reviews'],
                        summary = column['Summary'],
                        plays = column['Plays'],
                        playing = column['Playing'],
                        ratio_confiance = column['ratio_confiance'],
                        score = column['Score'],
                        genre = column['Genre'],
                        platform = column['Platform'],
                        date = column['Date']
                    )
        except Exception:
            self.stdout.write(self.style.ERROR('Error importing data'))
