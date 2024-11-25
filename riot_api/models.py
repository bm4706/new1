from django.db import models

class StreamerTier(models.Model):
    streamer_name = models.CharField(max_length=100)
    summoner_name = models.CharField(max_length=100)
    game_name = models.CharField(max_length=100)  # 추가
    tag_line = models.CharField(max_length=100)   # 추가
    tier = models.CharField(max_length=50)
    rank = models.CharField(max_length=50)
    league_points = models.IntegerField()
    wins = models.IntegerField()
    losses = models.IntegerField()
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.streamer_name} - {self.summoner_name}"
