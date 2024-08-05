# Generated by Django 5.0.7 on 2024-08-05 07:58

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "email",
                    models.EmailField(max_length=255, unique=True, verbose_name="이메일"),
                ),
                (
                    "nickname",
                    models.CharField(max_length=30, unique=True, verbose_name="닉네임"),
                ),
                ("password", models.CharField(max_length=255, verbose_name="비밀번호")),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="회원가입일"),
                ),
                (
                    "is_admin",
                    models.BooleanField(default=False, verbose_name="관리자 권한 여부"),
                ),
                (
                    "is_active",
                    models.BooleanField(default=True, verbose_name="계정 활성화 여부"),
                ),
                ("is_staff", models.BooleanField(default=False, verbose_name="스태브 여부")),
                (
                    "user_img",
                    models.ImageField(
                        default="user_defalt.jpg",
                        upload_to="user/user_img/%Y/%m/%D",
                        verbose_name="프로필 이미지",
                    ),
                ),
                (
                    "is_email_verified",
                    models.BooleanField(default=False, verbose_name="이메일 검증 여부"),
                ),
                (
                    "social_id",
                    models.CharField(
                        blank=True, max_length=30, null=True, verbose_name="소셜 아이디"
                    ),
                ),
                ("point", models.IntegerField(default=0)),
                (
                    "following",
                    models.ManyToManyField(
                        blank=True,
                        related_name="followers",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="팔로잉",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
