from django.core.management.base import BaseCommand
from riot_api.models import StreamerTier
from riot_api.riot_api import (
    get_puuid_by_riot_id,
    get_summoner_by_puuid,
    get_league_entries_by_summoner_id,
)
from django.conf import settings
import time


class Command(BaseCommand):
    help = 'Update streamer tiers by fetching data from Riot API'

    def handle(self, *args, **kwargs):
        streamer_tiers = StreamerTier.objects.all()

        for streamer in streamer_tiers:
            game_name = streamer.summoner_name.split('#')[0]
            tag_line = streamer.summoner_name.split('#')[1] if '#' in streamer.summoner_name else 'KR1'  # 기본 태그라인 설정
            print(f"Fetching PUUID for game_name: {game_name}, tag_line: {tag_line}")

            # PUUID 가져오기
            puuid = get_puuid_by_riot_id('asia', game_name, tag_line, settings.RIOT_API_KEY)
            if not puuid:
                self.stdout.write(self.style.WARNING(f'PUUID를 가져올 수 없습니다: {streamer.summoner_name}'))
                continue

            # 소환사 정보 가져오기
            summoner_info = get_summoner_by_puuid('kr', puuid, settings.RIOT_API_KEY)
            if not summoner_info:
                self.stdout.write(self.style.WARNING(f'소환사 정보를 가져올 수 없습니다: {streamer.summoner_name}'))
                continue

            encrypted_summoner_id = summoner_info.get('id')
            if not encrypted_summoner_id:
                self.stdout.write(self.style.WARNING(f'소환사 ID를 가져올 수 없습니다: {streamer.summoner_name}'))
                continue

            # 티어 정보 가져오기
            league_entries = get_league_entries_by_summoner_id('kr', encrypted_summoner_id, settings.RIOT_API_KEY)
            if not league_entries:
                self.stdout.write(self.style.WARNING(f'티어 정보를 가져올 수 없습니다: {streamer.summoner_name}'))
                continue

            # 가장 높은 티어 정보 선택 (예: 솔로 랭크)
            tier_info = None
            for entry in league_entries:
                if entry['queueType'] == 'RANKED_SOLO_5x5':
                    tier_info = entry
                    break
            if not tier_info:
                tier_info = league_entries[0]  # 솔로 랭크가 없을 경우 첫 번째 항목 사용

            # StreamerTier 객체 업데이트
            streamer.tier = tier_info['tier']
            streamer.rank = tier_info['rank']
            streamer.league_points = tier_info['leaguePoints']
            streamer.wins = tier_info['wins']
            streamer.losses = tier_info['losses']
            streamer.save()

            self.stdout.write(self.style.SUCCESS(f'업데이트 완료: {streamer.streamer_name}'))
            
            time.sleep(1) 
