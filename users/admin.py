from django.contrib import admin
from .models import User  # user 앱의 모델
from boards.models import Post  # board 앱의 모델 (예시로 Post)
from riot_api.models import StreamerTier  # summoner 앱의 모델 (예시로 SummonerStats)

# 각 모델을 Admin에 등록
admin.site.register(User)
admin.site.register(Post)  # board의 모델
admin.site.register(StreamerTier)  # summoner의 모델
