from django.urls import path
from users import views

urlpatterns = [
    path('signup/', views.SignupView.as_view()),
    path('auth/', views.AuthApiView.as_view()),
]
