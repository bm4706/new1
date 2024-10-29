from django import forms

class SummonerForm(forms.Form):
    game_name = forms.CharField(label='소환사명', max_length=30)
    tag_line = forms.CharField(label='태그라인', max_length=5, required=False)
