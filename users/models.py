from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin



class UserManager(BaseUserManager):
    ''' 사용자 모델을 생성하고 관리하는 클래스 입니다.'''


    def create_user(self, email, password, nickname):
        if not email:
            raise ValueError("유효하지 않은 이메일 형식입니다.")
        
        email = self.normalize_email(email)
        user = self.model(email=email, nickname=nickname)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, nickname):
        if not email:
            raise ValueError("유효하지 않은 이메일 형식입니다.")

        user = self.create_user(
            email=self.normalize_email(email), password=password, nickname=nickname
        )

        user.is_admin = True
        user.is_staff = True
        user.is_active = True
        user.is_email_verified =True
        user.save(using=self._db)
        return user

# 커스텀 유저 모델 정의
class User(AbstractBaseUser,PermissionsMixin):
  

    email = models.EmailField('이메일', max_length=255, unique=True)
    nickname = models.CharField('닉네임', max_length=30, unique=True)
    # password = models.CharField('비밀번호', max_length=255)
    created_at = models.DateTimeField('회원가입일', auto_now_add=True)
    is_admin = models.BooleanField('관리자 권한 여부', default=False)
    is_active = models.BooleanField('계정 활성화 여부', default=True)
    is_staff = models.BooleanField('스태브 여부', default=False)
    user_img = models.ImageField('프로필 이미지', upload_to='user/user_img/%Y/%m/%D', default='user_defalt.jpg')
    following = models.ManyToManyField('self', verbose_name='팔로잉', related_name='followers',symmetrical=False, blank=True)
    is_email_verified = models.BooleanField('이메일 검증 여부', default=False)
    social_id = models.CharField('소셜 아이디', max_length=30, blank=True, null=True)

    point = models.IntegerField(default=0)
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nickname']





    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True
