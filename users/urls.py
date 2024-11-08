from django.urls import path
from users import views

urlpatterns = [
    ## api
    
    path('signupAPI/', views.SignupAPIView.as_view()),
    path('auth/', views.AuthApiView.as_view()),
    
    
    ## html
    path('signup/', views.SignupView.as_view(),name='signup'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
]
