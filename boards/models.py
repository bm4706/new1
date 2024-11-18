from django.db import models
from users.models import User
from django.conf import settings

class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name='작성자')
    title = models.CharField('제목', max_length=100)
    content = models.TextField('내용')
    image = models.ImageField('이미지', upload_to='post/images/', blank=True, null=True)  # 이미지 필드 추가
    created_at = models.DateTimeField('작성일', auto_now_add=True)
    updated_at = models.DateTimeField('수정일', auto_now=True)

    def __str__(self):
        return self.title
    
    
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.SET_NULL, related_name='comments', null=True)  # 게시글과의 관계 설정
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)  # nullable 설정
    author_nickname = models.CharField(max_length=50, blank=True)  # 작성자의 닉네임을 저장하는 필드
    content = models.TextField('댓글 내용')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author_nickname}의 댓글"
    
    def save(self, *args, **kwargs):
        if self.author and not self.author_nickname:  # 닉네임이 비어있을 경우에만 설정
            self.author_nickname = self.author.nickname
        super().save(*args, **kwargs)
