"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from reviews import views as reviews_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('__debug__/', include('debug_toolbar.urls')),
    path('silk/', include('silk.urls', namespace='silk')),
    path('ratings/', reviews_views.show_ratings, name='show-ratings'),
    path('lab2/', reviews_views.lab2_queries, name='lab2-queries'),
    path('update-f/', reviews_views.update_ratings, name='update-f'),
    path('profiling/', reviews_views.profiling_view, name='profiling-view'),
    path('heavy-cache/', reviews_views.heavy_query_view, name='heavy-cache-view'),
    path('heavy-tasks/', reviews_views.heavy_tasks_view, name='heavy-tasks-view'),
]
