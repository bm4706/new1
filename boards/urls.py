from django.conf import settings
from django.conf.urls.static import static
from boards import views
from django.urls import path, include

urlpatterns = [
    path('posts/', views.ArticleView.as_view(), name='post-list-create'),
    path('posts/<int:pk>/', views.ArticleDetailView.as_view(), name='post-detail'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
