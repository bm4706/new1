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
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Post, Comment
from .forms import PostForm, CommentForm

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
class PostView(View):
    def get(self, request, pk=None):
        if pk:
            # 게시글 상세 조회
            post = get_object_or_404(Post, pk=pk)            
            comments = post.comments.all()  # 해당 게시글의 모든 댓글
            form = CommentForm()
            return render(request, 'boards/post_detail.html', {'post': post, 'comments': comments, 'form': form})
        else:
            # 게시글 목록 조회
            posts = Post.objects.all().order_by('-created_at')
            return render(request, 'boards/post_list.html', {'posts': posts})

        
    # 댓글 작성    
    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user  # 현재 로그인한 사용자를 작성자로 설정
            comment.post = post  # 댓글이 달린 게시글 설정
            comment.save()
            
            # 포인트 추가
            request.user.point += 1
            request.user.save()
            
            return redirect('post-detail', pk=post.pk)
        comments = post.comments.all()
        return render(request, 'boards/post_detail.html', {'post': post, 'comments': comments, 'form': form})

@method_decorator(login_required, name='dispatch')
class PostCreateView(View):
    def get(self, request):
        form = PostForm()
        return render(request, 'boards/post_create.html', {'form': form})

    def post(self, request):
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user  # 로그인된 사용자를 작성자로 설정
            post.save()
            
            # 포인트 증가
            request.user.point += 5
            request.user.save()
            
            return redirect('post-detail', pk=post.pk)  # 작성된 게시글로 리디렉션
        return render(request, 'boards/post_create.html', {'form': form})

@method_decorator(login_required, name='dispatch')
class PostEditView(View):
    def get(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        if post.author != request.user:
            return HttpResponseForbidden("수정 권한이 없습니다.")
        
        form = PostForm(instance=post)
        return render(request, 'boards/post_edit.html', {'form': form, 'post': post})  # post를 컨텍스트에 추가

    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        if post.author != request.user:
            return HttpResponseForbidden("수정 권한이 없습니다.")

        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, '게시글이 성공적으로 수정되었습니다.')
            return redirect('post-detail', pk=post.pk)  # pk 값을 명확히 전달
        return render(request, 'boards/post_edit.html', {'form': form, 'post': post})

@method_decorator(login_required, name='dispatch')
class PostDeleteView(View):
    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        if post.author != request.user:
            return HttpResponseForbidden("삭제 권한이 없습니다.")
        post.delete()
        request.user.point -= 5
        request.user.save()
        return redirect('post-list-create')


class CommentDeleteView(View):
    def post(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk)
        
        # 댓글 작성자만 삭제 가능
        if comment.author != request.user:
            return HttpResponseForbidden("삭제 권한이 없습니다.")
        
        comment.delete()
        
        # 포인트 차감
        request.user.point -= 1
        request.user.save()
        
        return redirect('post-detail', pk=comment.post.pk)
