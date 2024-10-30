from django import forms

class SummonerForm(forms.Form):
    game_name = forms.CharField(label='소환사명', max_length=30)
    tag_line = forms.CharField(label='태그라인', max_length=5, required=False)



class StreamerForm(forms.Form):
    streamer_name = forms.CharField(label='스트리머 닉네임', max_length=100, required=True)