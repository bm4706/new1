from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views  # 전체 views 모듈을 import하여 views.로 접근

urlpatterns = [
    # API 기반 뷰 URL 설정
    path('api/posts/', views.ArticleView.as_view()),  # 게시글 목록 조회 및 생성 (API)
    path('api/posts/<int:pk>/', views.ArticleDetailView.as_view()),  # 게시글 상세 조회, 수정, 삭제 (API)

    # HTML 기반 뷰 URL 설정
    path('', views.PostView.as_view(), name='post-list-create'),  # 게시글 목록 조회
    path('posts/create/', views.PostCreateView.as_view(), name='post-create'),  # 게시글 작성
    path('posts/<int:pk>/', views.PostView.as_view(), name='post-detail'),  # 게시글 상세 조회
    path('posts/<int:pk>/edit/', views.PostEditView.as_view(), name='post-edit'),  # 게시글 수정
    path('posts/<int:pk>/delete/', views.PostDeleteView.as_view(), name='post-delete'),  # 게시글 삭제
    path('comments/<int:pk>/delete/', views.CommentDeleteView.as_view(), name='comment-delete'),  # 댓글 삭제
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
