from django.db import models

TIERS = {
    'IRON': 1,
    'BRONZE': 2,
    'SILVER': 3,
    'GOLD': 4,
    'PLATINUM': 5,
    'DIAMOND': 6,
    'MASTER': 7,
    'GRANDMASTER': 8,
    'CHALLENGER': 9,
}

class StreamerTier(models.Model):
    streamer_name = models.CharField(max_length=100)
    summoner_name = models.CharField(max_length=100)
    game_name = models.CharField(max_length=100)  
    tag_line = models.CharField(max_length=100)   
    tier = models.CharField(max_length=50)
    rank = models.CharField(max_length=50)
    league_points = models.IntegerField()
    wins = models.IntegerField()
    losses = models.IntegerField()
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.streamer_name} - {self.summoner_name}"
    
    @property
    def tier_priority(self):
        return TIERS.get(self.tier.upper(), 0)
