from django.db import models

# Create your models here.
# reviews/models.py


class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Movie(models.Model):
    title = models.CharField(max_length=255)
    # علاقة Many-to-Many
    genres = models.ManyToManyField(Genre, related_name="movies")

    def __str__(self):
        return self.title

class Rating(models.Model):
    # علاقة Foreign Key
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="ratings")
    rating = models.FloatField()
    
    def __str__(self):
        return f"{self.movie.title}: {self.rating}"