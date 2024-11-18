from django.shortcuts import render, redirect
from django.conf import settings
from .riot_api import (
    get_puuid_by_riot_id,
    get_summoner_by_puuid,
    get_league_entries_by_summoner_id,
)
from .forms import SummonerForm, StreamerForm
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import StreamerTier
from django.core.paginator import Paginator

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

            # PUUID 가져오기
            puuid = get_puuid_by_riot_id(account_region, game_name, tag_line, api_key)
            if puuid:
                # 소환사 정보 가져오기
                summoner_info = get_summoner_by_puuid(region, puuid, api_key)
                if summoner_info:
                    encrypted_summoner_id = summoner_info.get('id')
                    if encrypted_summoner_id:
                        # 티어 정보 가져오기
                        league_entries = get_league_entries_by_summoner_id(region, encrypted_summoner_id, api_key)
                        if league_entries:
                            # 가장 높은 티어 정보 선택 (예: 솔로 랭크)
                            tier_info = None
                            for entry in league_entries:
                                if entry['queueType'] == 'RANKED_SOLO_5x5':
                                    tier_info = entry
                                    break
                            if not tier_info:
                                tier_info = league_entries[0]  # 솔로 랭크가 없을 경우 첫 번째 항목 사용

                            context = {
                                'game_name': game_name,
                                'tag_line': tag_line,
                                'puuid': puuid,
                                'summoner_info': summoner_info,
                                'tier_info': tier_info,
                                'streamer_form': StreamerForm(),  # 스트리머 폼 추가
                            }
                            # 세션에 필요한 데이터 저장
                            request.session['tier_info'] = tier_info
                            request.session['summoner_name'] = game_name
                            return render(request, 'riot_api/summoner_tier.html', context)
                        else:
                            error_message = "티어 정보를 가져올 수 없습니다."
                            return render(request, 'riot_api/error.html', {'error_message': error_message})
                    else:
                        error_message = "소환사 ID를 가져올 수 없습니다."
                        return render(request, 'riot_api/error.html', {'error_message': error_message})
                else:
                    error_message = "소환사 정보를 가져올 수 없습니다."
                    return render(request, 'riot_api/error.html', {'error_message': error_message})
            else:
                error_message = "PUUID를 가져올 수 없습니다. 닉네임과 태그라인을 확인하세요."
                return render(request, 'riot_api/error.html', {'error_message': error_message})
        else:
            form = SummonerForm()
            return render(request, 'riot_api/summoner_form.html', {'form': form})
    else:
        form = SummonerForm()
        return render(request, 'riot_api/summoner_form.html', {'form': form})
    
    
@csrf_exempt
def save_streamer_tier(request):
    if request.method == 'POST':
        # 티어 정보 저장 처리
        streamer_form = StreamerForm(request.POST)
        if streamer_form.is_valid():
            streamer_name = streamer_form.cleaned_data['streamer_name']
            # 세션에서 티어 정보 가져오기
            tier_info = request.session.get('tier_info')
            summoner_name = request.session.get('summoner_name')
            if tier_info and summoner_name:
                # StreamerTier 모델에 데이터 저장
                streamer_tier = StreamerTier.objects.create(
                    streamer_name=streamer_name,
                    summoner_name=summoner_name,
                    tier=tier_info['tier'],
                    rank=tier_info['rank'],
                    league_points=tier_info['leaguePoints'],
                    wins=tier_info['wins'],
                    losses=tier_info['losses'],
                )
                return redirect('streamer_tier_list')
            else:
                error_message = "티어 정보를 저장할 수 없습니다."
                return render(request, 'riot_api/error.html', {'error_message': error_message})
        else:
            error_message = "스트리머 닉네임을 입력해주세요."
            return render(request, 'riot_api/error.html', {'error_message': error_message})
    else:
        # POST 요청이 아닌 경우 에러 처리 또는 다른 처리를 할 수 있습니다.
        return redirect('summoner_tier')




def streamer_tier_list(request):
    query = request.GET.get('q')
    if query:
        streamer_tiers = StreamerTier.objects.filter(streamer_name__icontains=query)
        
        
    else:
        streamer_tiers = StreamerTier.objects.all()
       # 승률 계산 후 객체에 추가
    for tier in streamer_tiers:
        total_games = tier.wins + tier.losses
        tier.win_rate = (tier.wins / total_games * 100) if total_games > 0 else 0

    paginator = Paginator(streamer_tiers, 10)  # 페이지당 10개
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'riot_api/streamer_tier_list.html', {'page_obj': page_obj})