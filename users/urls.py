from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from users import views

urlpatterns = [
    ## api
    
    path('signupAPI/', views.SignupAPIView.as_view()),
    path('auth/', views.AuthApiView.as_view()),
    
    
    ## html
    path('signup/', views.SignupView.as_view(),name='signup'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout',),        
    path('profile/', views.ProfileView.as_view(), name='profile'), 
    path('profile/edit/', views.ProfileEditView.as_view(), name='profile-edit'),  # 프로필 수정 페이지
]
# 미디어 파일 접근을 위한 URL 설정 (개발 환경에서만)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)