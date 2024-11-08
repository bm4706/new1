from django.conf import settings
from django.conf.urls.static import static

from .views import ArticleView, ArticleDetailView, PostView
from django.urls import path, include

urlpatterns = [
    # API 기반 뷰 URL 설정
    path('api/posts/', ArticleView.as_view()),  # 게시글 목록 조회 및 생성 (API)
    path('api/posts/<int:pk>/', ArticleDetailView.as_view()),  # 게시글 상세 조회, 수정, 삭제 (API)

    # HTML 기반 뷰 URL 설정
    path('posts/', PostView.as_view(), name='post-list-create'),  # 게시글 목록 조회 및 생성
    path('posts/create/', PostView.as_view(), name='post-create'),  # 게시글 생성
    path('posts/<int:pk>/', PostView.as_view(), name='post-detail'),  # 게시글 상세 조회
    path('posts/<int:pk>/edit/', PostView.as_view(), name='post-edit'),  # 게시글 수정
    path('posts/<int:pk>/delete/', PostView.as_view(), name='post-delete'),  # 게시글 삭제
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
