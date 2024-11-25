from django import forms
from .models import StreamerTier

class SummonerForm(forms.Form):
    game_name = forms.CharField(label='소환사명', max_length=30)
    tag_line = forms.CharField(label='태그라인', max_length=5, required=False)



class StreamerForm(forms.ModelForm):
    class Meta:
        model = StreamerTier
        fields = ['streamer_name']  # 스트리머 닉네임만 입력받음