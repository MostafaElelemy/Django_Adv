from django.shortcuts import render

# Create your views here.

from .models import Rating, Movie

def show_ratings(request):

    # ---------------------------------------------
    # (أ) الكود اللي بيعمل مشكلة N+1
    # ---------------------------------------------
    print("--- RUNNING N+1 QUERY ---")
    ratings = Rating.objects.all()[:20] 

    for r in ratings:
        # هنا هيحصل 20 query زيادة
        print(f"Movie: {r.movie.title}") 

    # ---------------------------------------------
    # (ب) الكود المُحسن بـ select_related
    # ---------------------------------------------
    print("--- RUNNING select_related QUERY ---")
    ratings_optimized = Rating.objects.select_related('movie').all()[:20]

    for r in ratings_optimized:
        # هنا مفيش query جديد
        print(f"Movie: {r.movie.title}")

    # ---------------------------------------------
    # (ج) الكود المُحسن بـ prefetch_related (M2M)
    # ---------------------------------------------
    print("--- RUNNING prefetch_related QUERY ---")
    movies_optimized = Movie.objects.prefetch_related('genres').all()[:10]

    for m in movies_optimized:
        # هنا مفيش query جديد
        genres = [g.name for g in m.genres.all()]
        print(f"Movie: {m.title}, Genres: {genres}")


    # هنبعت الداتا دي للـ Template عشان نعرضها
    context = {
        'ratings_list': ratings_optimized
    }
    return render(request, 'reviews/ratings_page.html', context)