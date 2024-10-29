from django.urls import path
from . import views

urlpatterns = [
    path('summoner/', views.summoner_tier_view, name='summoner_tier'),
]
