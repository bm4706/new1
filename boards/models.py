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