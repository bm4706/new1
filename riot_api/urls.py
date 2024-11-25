from django.urls import path
from . import views

urlpatterns = [
    path('summoner/', views.summoner_tier_view, name='summoner_tier'),    
    path('save_streamer_tier/', views.save_streamer_tier, name='save_streamer_tier'),
    path('streamer_tiers/', views.streamer_tier_list, name='streamer_tier_list'),
    path('streamer_tier/delete/<int:pk>/', views.delete_streamer_tier, name='delete_streamer_tier'),  # 삭제 URL 추가
    path('streamer_tiers/update/', views.update_streamer_tiers, name='update_streamer_tiers'),  # 업데이트 URL 추가
]
