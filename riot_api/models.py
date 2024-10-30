from django.db import models

class StreamerTier(models.Model):
    streamer_name = models.CharField(max_length=100)  # 스트리머 닉네임
    summoner_name = models.CharField(max_length=30)  # 소환사 닉네임
    tier = models.CharField(max_length=20)  # 티어 (예: 'Gold', 'Platinum')
    rank = models.CharField(max_length=5)  # 랭크 (예: 'I', 'II')
    league_points = models.IntegerField()  # LP
    wins = models.IntegerField()  # 승리 횟수
    losses = models.IntegerField()  # 패배 횟수
    updated_at = models.DateTimeField(auto_now=True)  # 최근 업데이트 시간

    def __str__(self):
        return f"{self.streamer_name} - {self.tier} {self.rank} ({self.summoner_name})"