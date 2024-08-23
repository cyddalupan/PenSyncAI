from django.urls import path
from . import views

urlpatterns = [
    path('submit/', views.submit_article, name='submit_article'),
    path('submit/success/', views.submit_article_success, name='submit_article_success'),
]
