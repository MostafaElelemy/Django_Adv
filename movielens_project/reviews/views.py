from django.shortcuts import render
import cProfile
import pstats
import io
import time
from django.views.decorators.cache import cache_page
from django.core.cache import cache



from .models import Rating, Movie

def show_ratings(request):


    print("--- RUNNING N+1 QUERY ---")
    ratings = Rating.objects.all()[:20] 

    for r in ratings:
        
        print(f"Movie: {r.movie.title}") 

    
    print("--- RUNNING select_related QUERY ---")
    ratings_optimized = Rating.objects.select_related('movie').all()[:20]

    for r in ratings_optimized:
    
        print(f"Movie: {r.movie.title}")

    
    print("--- RUNNING prefetch_related QUERY ---")
    movies_optimized = Movie.objects.prefetch_related('genres').all()[:10]

    for m in movies_optimized:
        
        genres = [g.name for g in m.genres.all()]
        print(f"Movie: {m.title}, Genres: {genres}")


    
    context = {
        'ratings_list': ratings_optimized
    }
    return render(request, 'reviews/ratings_page.html', context)

from django.db.models import Q 


@cache_page(60 * 5) 
def lab2_queries(request):
    
    
    
    q_dark = Q(title__icontains='Dark')
    q_war = Q(title__icontains='War')
    movies_with_q = Movie.objects.filter(q_dark | q_war).distinct()[:10]

    
    
    movies_only_title = Movie.objects.only('title')[:10]
    print("\n--- Testing .only('title') ---")
    for m in movies_only_title:
        print(m.title) 
        

    
    
    movies_defer_title = Movie.objects.defer('title')[:10]
    print("\n--- Testing .defer('title') ---")
    
    for m in movies_defer_title:
        print(m.title) 

    
    ratings_dict = Rating.objects.filter(rating=5.0).values('rating', 'movie__title')[:10]
    
    
    ratings_tuple = Rating.objects.filter(rating=5.0).values_list('rating', 'movie__title')[:10]

    context = {
        'movies_with_q': movies_with_q,
        'ratings_dict': ratings_dict,
        'ratings_tuple': ratings_tuple,
    }
    return render(request, 'reviews/lab2_page.html', context)



from django.db.models import Q, F 
from django.http import HttpResponse



def update_ratings(request):
    
    
    
    
    count_before = Rating.objects.filter(rating=4.0).count()
    
    
    
    updated_count = Rating.objects.filter(rating=4.0).update(rating=F('rating') + 0.1)
    
    
    count_after = Rating.objects.filter(rating=4.0).count()
    
    
    count_new = Rating.objects.filter(rating=4.1).count()

    response_text = f"""
    <h1>Updating with F() Expression</h1>
    <p>Ratings with 4.0 (Before): {count_before}</p>
    <p>Ratings updated: {updated_count}</p>
    <p>Ratings with 4.0 (After): {count_after}</p>
    <p>Ratings with 4.1 (Now): {count_new}</p>
    <br>
   
    """
    return HttpResponse(response_text)

def profile_view(func):
    
    def wrapper(request, *args, **kwargs):
        
        pr = cProfile.Profile()
        pr.enable()
        
        
        response = func(request, *args, **kwargs)
        
        
        pr.disable()
        
        
        s = io.StringIO()
        sortby = 'cumulative' 
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats(30) 
        
        print("\n" + "="*80)
        print(f"--- cProfile Results for: {func.__name__} ---")
        print(s.getvalue())
        print("="*80 + "\n")
        
        return response
    return wrapper








@profile_view  
def profiling_view(request):
    
    
    
    time.sleep(0.1) 

    
    
    ratings = Rating.objects.select_related('movie').all()[:20]
    

    ratings_data = []
    for r in ratings:
        ratings_data.append({
            'title': r.movie.title, 
            'rating': r.rating
        })

    context = {
        'ratings_list': ratings_data
    }
    return render(request, 'reviews/profiling_page.html', context)

def heavy_query_view(request):
    
    
    cache_key = 'heavy_movie_stats'
    
    
    stats = cache.get(cache_key)
    
    if stats is None:
        
    
        print("--- CACHE MISS! Running the heavy ORM query... ---")
        
         
        time.sleep(1.5) 
        
        all_genres = Genre.objects.all()
        stats = {
            'total_genres': all_genres.count(),
            'genre_names': [g.name for g in all_genres]
        }
        
        cache.set(cache_key, stats, timeout=60 * 5)
    else:
        print("--- CACHE HIT! Serving data from Redis... ---")

    context = {
        'stats': stats
    }
    return render(request, 'reviews/heavy_query_page.html', context)

from .tasks import generate_report_task, send_welcome_email_task

def heavy_tasks_view(request):
    
    
    print("--- Offloading tasks to Celery... ---")
    
    generate_report_task.delay(user_id=1) 
    
    send_welcome_email_task.delay(user_email="mostafa@lab.com", message="Hello")

    
    return HttpResponse("<h2>المهام بتاعتك اتحدفت في الخلفية!</h2><p>الصفحة ردت في أقل من ثانية. بص على الـ Worker و Flower.</p>")