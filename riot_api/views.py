from django.shortcuts import get_object_or_404, render, redirect
from django.conf import settings
from .riot_api import (
    get_puuid_by_riot_id,
    get_summoner_by_puuid,
    get_league_entries_by_summoner_id,
)
from .forms import SummonerForm, StreamerForm
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseForbidden, JsonResponse
from .models import StreamerTier
from django.core.paginator import Paginator
from django.core.cache import cache
from django.contrib.auth.decorators import login_required
from django.db.models import F, ExpressionWrapper, FloatField

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
                                'is_superuser': request.user.is_superuser,  # 슈퍼유저 여부 추가
                            }
                            # 세션에 필요한 데이터 저장
                            request.session['tier_info'] = tier_info
                            request.session['tag_line'] = tag_line
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
                error_message = "소환사 닉네임과 태그라인을 확인하세요."
                return render(request, 'riot_api/error.html', {'error_message': error_message})
        else:
            form = SummonerForm()
            return render(request, 'riot_api/summoner_form.html', {'form': form})
    else:
        form = SummonerForm()
        return render(request, 'riot_api/summoner_form.html', {'form': form})

@csrf_exempt
def save_streamer_tier(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden("이 작업은 관리자만 수행할 수 있습니다.")

    if request.method == 'POST':
        # 세션 데이터 확인
        game_name = request.session.get('summoner_name')
        tag_line = request.session.get('tag_line')
        tier_info = request.session.get('tier_info')

        # 로그 추가
        print(f"세션 데이터 확인: game_name={game_name}, tag_line={tag_line}, tier_info={tier_info}")

        if not game_name or not tag_line or not tier_info:
            return render(request, 'riot_api/error.html', {'error_message': "필수 정보가 누락되었습니다. 다시 시도해주세요."})

        # 스트리머 폼 데이터 확인 및 저장
        streamer_form = StreamerForm(request.POST)
        if streamer_form.is_valid():
            streamer_name = streamer_form.cleaned_data['streamer_name']
            # `StreamerTier` 데이터 저장
            StreamerTier.objects.create(
                streamer_name=streamer_name,
                summoner_name=f"{game_name}#{tag_line}",  # 태그라인 포함한 소환사 이름 저장
                game_name=game_name,  # 소환사 이름
                tag_line=tag_line,
                tier=tier_info['tier'],
                rank=tier_info['rank'],
                league_points=tier_info['leaguePoints'],
                wins=tier_info['wins'],
                losses=tier_info['losses'],
            )
            return redirect('streamer_tier_list')
        else:
            return render(request, 'riot_api/error.html', {'error_message': "스트리머 닉네임이 유효하지 않습니다."})
    else:
        return redirect('summoner_tier')


def streamer_tier_list(request):
    query = request.GET.get('q')
    sort_order = request.GET.get('sort', 'alphabetical')  # 기본 정렬 기준은 알파벳순

    if query:
        streamer_tiers = StreamerTier.objects.filter(streamer_name__icontains=query)
    else:
        streamer_tiers = StreamerTier.objects.all()

    # 승률 계산 후 객체에 추가
    streamer_tiers = streamer_tiers.annotate(
        win_rate=ExpressionWrapper(
            F('wins') * 100 / (F('wins') + F('losses')),
            output_field=FloatField()
        )
    )

    # 정렬 기준 적용
    if sort_order == 'tier_desc':
        streamer_tiers = sorted(streamer_tiers, key=lambda x: (x.tier_priority, -x.league_points), reverse=True)
    elif sort_order == 'tier_asc':
        streamer_tiers = sorted(streamer_tiers, key=lambda x: (x.tier_priority, x.league_points))
    elif sort_order == 'alphabetical':
        streamer_tiers = streamer_tiers.order_by('streamer_name')

    paginator = Paginator(streamer_tiers, 10)  # 페이지당 10개
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'riot_api/streamer_tier_list.html', {
        'page_obj': page_obj,
        'is_superuser': request.user.is_superuser,
        'sort_order': sort_order,  # 현재 정렬 기준 전달
        'query': query,  # 현재 검색어 전달
    })



def delete_streamer_tier(request, pk):
    if not request.user.is_superuser:  # 슈퍼유저 권한 확인
        return HttpResponseForbidden("이 작업은 관리자만 수행할 수 있습니다.")

    streamer_tier = get_object_or_404(StreamerTier, pk=pk)
    streamer_tier.delete()  # 데이터 삭제
    return redirect('streamer_tier_list')  # 스트리머 티어 리스트로 리디렉션



def update_streamer_tiers(request):
    if request.method != 'POST':
        return JsonResponse({"status": "error", "message": "올바른 요청이 아닙니다. 다시 시도해주세요."}, status=405)
    # 요청 제한 (캐시 키 생성)
    cache_key = f"update_tiers_{request.user.id}"
    if cache.get(cache_key):
        return JsonResponse({"status": "error", "message": "잠시 후 다시 시도해주세요."}, status=429)


    messages = []
    streamer_tiers = StreamerTier.objects.all()

    for streamer in streamer_tiers:
        game_name = streamer.game_name
        tag_line = streamer.tag_line

        # PUUID 가져오기
        puuid = get_puuid_by_riot_id('asia', game_name, tag_line, settings.RIOT_API_KEY)
        if not puuid:
            messages.append(f"PUUID를 가져올 수 없습니다: {streamer.summoner_name}")
            continue

        # 소환사 정보 가져오기
        summoner_info = get_summoner_by_puuid('kr', puuid, settings.RIOT_API_KEY)
        if not summoner_info:
            messages.append(f"소환사 정보를 가져올 수 없습니다: {streamer.summoner_name}")
            continue

        encrypted_summoner_id = summoner_info.get('id')
        if not encrypted_summoner_id:
            messages.append(f"소환사 ID를 가져올 수 없습니다: {streamer.summoner_name}")
            continue

        # 티어 정보 가져오기
        league_entries = get_league_entries_by_summoner_id('kr', encrypted_summoner_id, settings.RIOT_API_KEY)
        if not league_entries:
            messages.append(f"티어 정보를 가져올 수 없습니다: {streamer.summoner_name}")
            continue

        # 가장 높은 티어 정보 선택
        tier_info = None
        for entry in league_entries:
            if entry['queueType'] == 'RANKED_SOLO_5x5':
                tier_info = entry
                break
        if not tier_info:
            tier_info = league_entries[0]

        # StreamerTier 객체 업데이트
        streamer.tier = tier_info['tier']
        streamer.rank = tier_info['rank']
        streamer.league_points = tier_info['leaguePoints']
        streamer.wins = tier_info['wins']
        streamer.losses = tier_info['losses']
        streamer.save()

        messages.append(f"업데이트 완료: {streamer.streamer_name}")
    # 요청 제한 시간 설정 (1분)
    cache.set(cache_key, True, timeout=60)
    # 리디렉션으로 티어 목록 페이지로 이동
    return redirect('streamer_tier_list')

