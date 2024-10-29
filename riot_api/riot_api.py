
import requests

def get_puuid_by_riot_id(region, game_name, tag_line, api_key):
    url = f"https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
    headers = {"X-Riot-Token": api_key}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data['puuid']
    else:
        print(f"Error fetching PUUID: {response.status_code}")
        return None

def get_summoner_by_puuid(region, puuid, api_key):
    url = f"https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}"
    headers = {
        "X-Riot-Token": api_key
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data  # 소환사 정보를 반환
    else:
        print(f"Error fetching summoner info: {response.status_code} - {response.text}")
        return None

def get_league_entries_by_summoner_id(region, encrypted_summoner_id, api_key):
    url = f"https://{region}.api.riotgames.com/lol/league/v4/entries/by-summoner/{encrypted_summoner_id}"
    headers = {
        "X-Riot-Token": api_key
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data  # 티어 정보를 포함한 리스트 반환
    else:
        print(f"Error fetching league entries: {response.status_code} - {response.text}")
        return None