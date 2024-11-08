from django.http import HttpResponseForbidden
from rest_framework import generics, permissions
from .models import Post
from .serializers import PostSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import render, get_object_or_404, redirect
from rest_framework import status, permissions
from django.contrib.auth.decorators import login_required
from .forms import PostForm

from rest_framework.exceptions import PermissionDenied, NotFound

from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth.decorators import login_required
from .models import Post
from .forms import PostForm

### apiview 기반
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









### html 기반
@method_decorator(login_required, name='dispatch')
class PostView(View):
    def get(self, request, pk=None):
        if pk:
            # 게시글 상세 조회
            post = get_object_or_404(Post, pk=pk)
            return render(request, 'boards/post_detail.html', {'post': post})
        else:
            # 게시글 목록 조회
            posts = Post.objects.all().order_by('-created_at')
            return render(request, 'boards/post_list.html', {'posts': posts})

    def post(self, request, pk=None):
        if pk:
            # 게시글 수정
            post = get_object_or_404(Post, pk=pk)
            if post.author != request.user:
                return HttpResponseForbidden("수정 권한이 없습니다.")
            form = PostForm(request.POST, instance=post)
            if form.is_valid():
                form.save()
                return redirect('post-detail', pk=post.pk)
        else:
            # 게시글 생성
            form = PostForm(request.POST)
            if form.is_valid():
                post = form.save(commit=False)
                post.author = request.user
                post.save()
                # 포인트 증가
                request.user.point += 5
                request.user.save()
                return redirect('post-detail', pk=post.pk)
        form = PostForm()
        return render(request, 'boards/post_form.html', {'form': form})

    def delete(self, request, pk):
        # 게시글 삭제
        post = get_object_or_404(Post, pk=pk)
        if post.author != request.user:
            return HttpResponseForbidden("삭제 권한이 없습니다.")
        post.delete()
        # 포인트 감소
        request.user.point -= 5
        request.user.save()
        return redirect('post-list-create')


