from django.db import models

class Game(models.Model):
    name = models.CharField(max_length=255)
    release_date = models.CharField(max_length=255)
    number_of_reviews = models.CharField(max_length=255)
    summary = models.CharField(max_length=255)
    plays = models.CharField(max_length=255)
    playing = models.CharField(max_length=255)
    ratio_confiance = models.CharField(max_length=255)
    score = models.CharField(max_length=255)
    genre = models.CharField(max_length=255)
    platform = models.CharField(max_length=255)
    date = models.CharField(max_length=255)
