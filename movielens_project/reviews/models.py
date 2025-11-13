# reviews/models.py
from django.db import models

class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Movie(models.Model):
    title = models.CharField(max_length=255)
    genres = models.ManyToManyField(Genre, related_name="movies")

    def __str__(self):
        return self.title
    
    
    
    class Meta:
        indexes = [
            models.Index(fields=['title']),
        ]

class Rating(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="ratings")
    
    
    
    rating = models.FloatField(db_index=True)
    
    def __str__(self):
        return f"{self.movie.title}: {self.rating}"