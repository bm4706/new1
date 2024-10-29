from django.shortcuts import render
from django.conf import settings
from .riot_api import (
    get_puuid_by_riot_id,
    get_summoner_by_puuid,
    get_league_entries_by_summoner_id,
)
from .forms import SummonerForm
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

@csrf_exempt
def summoner_tier_view(request):
    if request.method == 'GET':
        form = SummonerForm(request.GET)
        if form.is_valid():
            api_key = settings.RIOT_API_KEY
            account_region = 'asia'
            region = 'kr'  # 게임 서버 지역 설정
            game_name = form.cleaned_data['game_name']
            tag_line = form.cleaned_data['tag_line'] or 'KR1'
            
            # 1. PUUID 가져오기
            puuid = get_puuid_by_riot_id(account_region, game_name, tag_line, api_key)
            if puuid:
                # 2. 소환사 정보 가져오기
                summoner_info = get_summoner_by_puuid(region, puuid, api_key)
                if summoner_info:
                    encrypted_summoner_id = summoner_info.get('id')
                    # 3. 티어 정보 가져오기
                    if encrypted_summoner_id:
                        league_entries = get_league_entries_by_summoner_id(region, encrypted_summoner_id, api_key)
                        if league_entries:
                            context = {
                                'game_name': game_name,
                                'tag_line': tag_line,
                                'puuid': puuid,
                                'summoner_info': summoner_info,
                                'league_entries': league_entries,
                            }
                            return render(request, 'riot_api/summoner_tier.html', context)
                        else:
                            error_message = "티어 정보를 가져올 수 없습니다."
                    else:
                        error_message = "소환사 ID를 가져올 수 없습니다."
                else:
                    error_message = "소환사 정보를 가져올 수 없습니다."
            else:
                error_message = "PUUID를 가져올 수 없습니다. 닉네임과 태그라인을 확인하세요."
            return render(request, 'riot_api/error.html', {'error_message': error_message})
    else:
        form = SummonerForm()
    return render(request, 'riot_api/summoner_form.html', {'form': form})