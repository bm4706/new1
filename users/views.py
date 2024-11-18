import jwt
from django.shortcuts import render, get_object_or_404, redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
# from django.contrib.auth.models import User
from users.models import User
from django.contrib.auth import authenticate, login, logout
from rest_framework_simplejwt.tokens import RefreshToken
from users.serializers import UserSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from .serializers import UserSerializer
from new1.settings import SECRET_KEY
from django.views import View
from django.contrib import messages
from .forms import RegisterForm, ProfileForm


from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from boards.models import Post, Comment 
from django.core.paginator import Paginator

# 회원가입 클래스

class SignupAPIView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            
            # jwt 토큰 접근
            token = TokenObtainPairSerializer.get_token(user)
            refresh_token = str(token)
            access_token = str(token.access_token)
            res = Response(
                {
                    "user": serializer.data,
                    "message": "등록 성공",
                    "token": {
                        "access": access_token,
                        "refresh": refresh_token,
                    },
                },
                status=status.HTTP_201_CREATED,
            )
            
            # jwt 토큰 => 쿠키에 저장
            res.set_cookie("access", access_token, httponly=True)
            res.set_cookie("refresh", refresh_token, httponly=True)
            
            return res
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class AuthApiView(APIView):
    # 유저 정보 확인
    def get(self, request):
        try:
            # access token을 decode 해서 유저 id 추출 => 유저 식별
            access = request.COOKIES['access']
            payload = jwt.decode(access, SECRET_KEY, algorithms=['HS256'])
            pk = payload.get('user_id')
            user = get_object_or_404(User, pk=pk)
            serializer = UserSerializer(instance=user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except(jwt.exceptions.ExpiredSignatureError):
            # 토큰 만료 시 토큰 갱신
            data = {'refresh': request.COOKIES.get('refresh', None)}
            serializer = TokenRefreshSerializer(data=data)
            if serializer.is_valid(raise_exception=True):
                access = serializer.data.get('access', None)
                refresh = serializer.data.get('refresh', None)
                payload = jwt.decode(access, SECRET_KEY, algorithms=['HS256'])
                pk = payload.get('user_id')
                user = get_object_or_404(User, pk=pk)
                serializer = UserSerializer(instance=user)
                res = Response(serializer.data, status=status.HTTP_200_OK)
                res.set_cookie('access', access)
                res.set_cookie('refresh', refresh)
                return res
            raise jwt.exceptions.InvalidTokenError

        except(jwt.exceptions.InvalidTokenError):
            # 사용 불가능한 토큰일 때
            return Response(status=status.HTTP_400_BAD_REQUEST)

    # 로그인
    def post(self, request):
    	# 유저 인증
        user = authenticate(
            email=request.data.get("email"), password=request.data.get("password")
        )
        # 이미 회원가입 된 유저일 때
        if user is not None:
            serializer = UserSerializer(user)
            # jwt 토큰 접근
            token = TokenObtainPairSerializer.get_token(user)
            refresh_token = str(token)
            access_token = str(token.access_token)
            res = Response(
                {
                    "user": serializer.data,
                    "message": "로그인 성공",
                    "token": {
                        "access": access_token,
                        "refresh": refresh_token,
                    },
                },
                status=status.HTTP_200_OK,
            )
            # jwt 토큰 => 쿠키에 저장
            res.set_cookie("access", access_token, httponly=True)
            res.set_cookie("refresh", refresh_token, httponly=True)
            return res
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    # 로그아웃
    def delete(self, request):
        # 쿠키에 저장된 토큰 삭제 => 로그아웃 처리
        response = Response({
            "message": "Logout success"
            }, status=status.HTTP_202_ACCEPTED)
        response.delete_cookie("access")
        response.delete_cookie("refresh")
        return response
    
    
    
class LoginView(View):
    def get(self, request):
        return render(request, 'users/login.html')

    def post(self, request):
        # 폼에서 전송된 데이터 가져오기
        email = request.POST.get('email')
        password = request.POST.get('password')

        # 유저 인증
        user = authenticate(email=email, password=password)

        if user is not None:
            login(request, user)  # 로그인 세션 생성
            messages.success(request, '로그인에 성공하였습니다.')
            return redirect('post-list-create')
        else:
            messages.error(request, '이메일 또는 비밀번호가 올바르지 않습니다.')
            return render(request, 'users/login.html')
        
        

class SignupView(View):
    def get(self, request):
        form = RegisterForm()
        return render(request, 'users/signup.html', {'form': form})

    def post(self, request):
        form = RegisterForm(request.POST, request.FILES)  # 이미지 파일 포함
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, '회원가입에 성공하였습니다.')
            return redirect('login')
        else:
            messages.error(request, '회원가입에 실패하였습니다.')
            return render(request, 'users/signup.html', {'form': form})


class LogoutView(View):
    def post(self, request):
        logout(request)  # 사용자 로그아웃
        messages.success(request, '로그아웃되었습니다.')
        return redirect('post-list-create') 
    
    
    
@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    def get(self, request):
        # 사용자가 작성한 글 가져오기
        user_posts = Post.objects.filter(author=request.user).order_by('-created_at')
        post_paginator = Paginator(user_posts, 10)  # 10개씩 페이지네이션
        post_page_number = request.GET.get('post_page')
        post_page = post_paginator.get_page(post_page_number)

        # 사용자가 작성한 댓글 가져오기
        user_comments = Comment.objects.filter(author=request.user).order_by('-created_at')
        comment_paginator = Paginator(user_comments, 10)  # 10개씩 페이지네이션
        comment_page_number = request.GET.get('comment_page')
        comment_page = comment_paginator.get_page(comment_page_number)

        return render(request, 'users/profile.html', {
            'post_page': post_page,
            'comment_page': comment_page,
        })
    
@method_decorator(login_required, name='dispatch')
class ProfileEditView(View):
    def get(self, request):
        form = ProfileForm(instance=request.user)
        return render(request, 'users/profile_edit.html', {'form': form})

    def post(self, request):
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            user = form.save(commit=False)  # 데이터베이스 저장 전 임시 저장
            # 닉네임이나 이미지를 변경하지 않은 경우 기존 값을 유지
            if not form.cleaned_data.get('user_img'):  # 이미지가 없으면
                user.user_img = request.user.user_img  # 기존 이미지 유지
            if not form.cleaned_data.get('nickname'):  # 닉네임이 없으면
                user.nickname = request.user.nickname  # 기존 닉네임 유지
            user.save()  # 변경 사항 저장
            return redirect('profile')
        
        # 폼 유효성 검사 실패 시 오류 메시지 표시
        return render(request, 'users/profile_edit.html', {'form': form, 'errors': form.errors})