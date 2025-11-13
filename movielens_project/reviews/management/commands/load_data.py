import csv
from django.core.management.base import BaseCommand
from reviews.models import Movie, Genre, Rating # غيرنا اسم الـ app

class Command(BaseCommand):
    help = 'Loads data from MovieLens dataset'

    def handle(self, *args, **options):
        # *** حط ملفات الـ CSV جنب ملف manage.py عشان المسارات دي تشتغل ***
        MOVIES_CSV = 'movies.csv'
        RATINGS_CSV = 'ratings.csv'

        self.stdout.write("Deleting old data...")
        Genre.objects.all().delete()
        Movie.objects.all().delete()
        Rating.objects.all().delete()

        # (1) تحميل الأفلام والجانرا
        self.stdout.write("Loading movies and genres...")
        movie_id_map = {} # ديكشنري عشان نربط ID الفيلم من الـ CSV بالـ ID الجديد في الداتابيز

        with open(MOVIES_CSV, encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader) # skip header

            for row in reader:
                csv_movie_id, title, genres_str = row[0], row[1], row[2]

                movie = Movie.objects.create(title=title)
                movie_id_map[csv_movie_id] = movie.id # ربطنا الـ ID القديم بالجديد

                genres_list = genres_str.split('|')
                for genre_name in genres_list:
                    if genre_name != "(no genres listed)":
                        genre, created = Genre.objects.get_or_create(name=genre_name)
                        movie.genres.add(genre)

        # (2) تحميل التقييمات
        self.stdout.write("Loading ratings...")
        ratings_to_create = []
        with open(RATINGS_CSV, encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader) # skip header

            for row in reader:
                user_id, csv_movie_id, rating_val = row[0], row[1], row[2]

                # نستخدم الـ ID الجديد للفيلم من الديكشنري
                db_movie_id = movie_id_map.get(csv_movie_id)

                if db_movie_id: # لو الفيلم موجود
                    ratings_to_create.append(
                        Rating(movie_id=db_movie_id, rating=float(rating_val))
                    )

            Rating.objects.bulk_create(ratings_to_create, batch_size=1000)

        self.stdout.write(self.style.SUCCESS('Data loaded successfully!'))