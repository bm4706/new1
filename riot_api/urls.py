from django.urls import path
from . import views

urlpatterns = [
    path('summoner/', views.summoner_tier_view, name='summoner_tier'),    
    path('save_streamer_tier/', views.save_streamer_tier, name='save_streamer_tier'),
    path('streamer_tiers/', views.streamer_tier_list, name='streamer_tier_list'),
]
