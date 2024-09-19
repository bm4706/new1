from rest_framework import generics, permissions
from .models import Post
from .serializers import PostSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from rest_framework.exceptions import PermissionDenied, NotFound
# Create your models here.
class ArticleView(APIView):
    
    # 권한 관리 (로그인시 읽기쓰기가능, 비로그인시 읽기만)
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    # 게시글 조회
    def get(self, request):
        posts = Post.objects.all().order_by('-created_at') # 내림차순 정렬
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            post = serializer.save(author=request.user)
            # 포인트 증가
            user = request.user
            user.point += 5
            user.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
# 상세 게시물
class ArticleDetailView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    # 객체 가져오기 헬퍼 메서드
    def get_object(self, pk):
        try:
            return Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            raise NotFound("해당 게시글을 찾을 수 없습니다.")

    # 게시글 상세 조회 (GET 요청)
    def get(self, request, pk):
        post = self.get_object(pk)
        serializer = PostSerializer(post)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 게시글 수정 (PUT 요청)
    def put(self, request, pk):
        post = self.get_object(pk)
        if post.author != request.user:
            raise PermissionDenied("수정 권한이 없습니다.")
        serializer = PostSerializer(post, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 게시글 삭제 (DELETE 요청)
    def delete(self, request, pk):
        post = self.get_object(pk)
        if post.author != request.user:
            raise PermissionDenied("삭제 권한이 없습니다.")
        post.delete()
        # 포인트 감소
        user = request.user
        user.point -= 5
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
