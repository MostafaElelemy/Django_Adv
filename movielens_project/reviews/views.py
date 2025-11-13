from django.shortcuts import render
import cProfile
import pstats
import io
import time

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

# reviews/views.py
# ... (متنساش تسيب الـ imports والـ view القديم فوق)
from django.db.models import Q # <--- (1) ضيف الـ import ده فوق خالص

# ... (سيب view بتاع show_ratings زي ما هو) ...

# (2) --- ضيف الـ view الجديد ده تحته ---
def lab2_queries(request):
    
    # 1. استخدام Q() object
    # هنجيب الأفلام اللي عنوانها فيه "Dark" أو "War"
    q_dark = Q(title__icontains='Dark')
    q_war = Q(title__icontains='War')
    movies_with_q = Movie.objects.filter(q_dark | q_war).distinct()[:10]

    # 3. استخدام only() - هات الـ title بس
    # (بص على الترمينال اللي شغال فيه runserver، هتلاقي كويري واحد بس)
    movies_only_title = Movie.objects.only('title')[:10]
    print("\n--- Testing .only('title') ---")
    for m in movies_only_title:
        print(m.title) # سريع (موجود)
        # لو حاولت تستخدم m.genres هيعمل كويري جديد (عشان ده M2M)

    # 3. استخدام defer() - هات كله ما عدا الـ title
    # (بص على الترمينال، هتلاقي كويري لكل لفة عشان يجيب الـ title)
    movies_defer_title = Movie.objects.defer('title')[:10]
    print("\n--- Testing .defer('title') ---")
    print("!!! (هنا هيحصل N+1 queries) !!!")
    for m in movies_defer_title:
        print(m.title) # بطيء (بيعمل كويري جديد كل مرة)

    # 4. استخدام values() - عشان نجيب dict
    ratings_dict = Rating.objects.filter(rating=5.0).values('rating', 'movie__title')[:10]
    
    # 5. استخدام values_list() - عشان نجيب tuple
    ratings_tuple = Rating.objects.filter(rating=5.0).values_list('rating', 'movie__title')[:10]

    context = {
        'movies_with_q': movies_with_q,
        'ratings_dict': ratings_dict,
        'ratings_tuple': ratings_tuple,
    }
    return render(request, 'reviews/lab2_page.html', context)

# reviews/views.py
# ... (متنساش تسيب الـ imports والـ views القديمة فوق)
from django.db.models import Q, F # <--- (1) ضيف الـ F هنا مع الـ Q
from django.http import HttpResponse

# ... (سيب الـ views التانية زي ما هي) ...

# (2) --- ضيف الـ view الجديد ده ---
def update_ratings(request):
    # 2. استخدام F()
    # هنزود 0.1 على كل التقييمات اللي قيمتها 4.0
    
    # الأول، نشوف عددهم كام
    count_before = Rating.objects.filter(rating=4.0).count()
    
    # نفذ الـ UPDATE في كويري واحد (سريييع جداً)
    # SQL: UPDATE reviews_rating SET rating = rating + 0.1 WHERE rating = 4.0;
    updated_count = Rating.objects.filter(rating=4.0).update(rating=F('rating') + 0.1)
    
    # نشوف عددهم بقى كام
    count_after = Rating.objects.filter(rating=4.0).count()
    
    # نشوف الداتا الجديدة (4.1)
    count_new = Rating.objects.filter(rating=4.1).count()

    response_text = f"""
    <h1>Updating with F() Expression</h1>
    <p>Ratings with 4.0 (Before): {count_before}</p>
    <p>Ratings updated: {updated_count}</p>
    <p>Ratings with 4.0 (After): {count_after}</p>
    <p>Ratings with 4.1 (Now): {count_new}</p>
    <br>
    <p>... اعمل ريفرش عشان تنفذ الكود تاني (هتلاقي الأرقام اتغيرت) ...</p>
    """
    return HttpResponse(response_text)

def profile_view(func):
    """
    Decorator بسيط بيشغل cProfile على أي View
    وبيطبع النتيجة في الكونسول (الترمينال).
    """
    def wrapper(request, *args, **kwargs):
        # ابدأ الـ Profiler
        pr = cProfile.Profile()
        pr.enable()
        
        # شغل الـ View الأصلي
        response = func(request, *args, **kwargs)
        
        # وقف الـ Profiler
        pr.disable()
        
        # اطبع النتايج في الترمينال
        s = io.StringIO()
        sortby = 'cumulative' # رتب بالوقت التراكمي
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats(30) # اطبع أهم 30 function
        
        print("\n" + "="*80)
        print(f"--- cProfile Results for: {func.__name__} ---")
        print(s.getvalue())
        print("="*80 + "\n")
        
        return response
    return wrapper


# ... (سيب الـ views القديمة بتاعتك زي ما هي) ...
# show_ratings, lab2_queries, update_ratings


# --- (3) ضيف الـ View "البطيء" ده ---
# ده الـ View اللي هنطبق عليه اللاب
@profile_view  # <--- شغل الـ Profiler بتاعنا عليه
def profiling_view(request):
    
    # (أ) مشكلة "دالة بطيئة" (زي API call أو حسبة معقدة)
    # هنخلي الكود "ينام" 0.1 ثانية عشان نشوفها في التحليل
    time.sleep(0.1) 

    # (ب) مشكلة "N+1 Query" (اللي اكتشفناها في لاب 1)
    # ده الكود الكويس دلوقتي
    ratings = Rating.objects.select_related('movie').all()[:20]
    
    # بنحضر الداتا عشان نعرضها في الـ Template
    ratings_data = []
    for r in ratings:
        ratings_data.append({
            'title': r.movie.title, # <--- دي اللي بتعمل N+1
            'rating': r.rating
        })

    context = {
        'ratings_list': ratings_data
    }
    return render(request, 'reviews/profiling_page.html', context)