from django import forms
from .models import User
from django.core.exceptions import ValidationError
from django.forms.widgets import ClearableFileInput

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label='비밀번호')
    password2 = forms.CharField(widget=forms.PasswordInput, label="비밀번호 확인")

    class Meta:
        model = User
        fields = ['email', 'nickname', 'password', 'user_img']  # 필드 목록
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("이미 사용 중인 이메일입니다. 다른 이메일을 입력해주세요.")
        return email

    def clean_nickname(self):
        nickname = self.cleaned_data.get('nickname')
        if User.objects.filter(nickname=nickname).exists():
            raise ValidationError("이미 사용 중인 닉네임입니다. 다른 닉네임을 입력해주세요.")
        return nickname
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password2 = cleaned_data.get("password2")

        if password != password2:
            self.add_error('password2', "비밀번호가 일치하지 않습니다.")
        return cleaned_data

class CustomClearableFileInput(ClearableFileInput):
    clear_checkbox_label = "이미지 제거"
    initial_text = ""
    input_text = "이미지 변경"

class ProfileForm(forms.ModelForm):
    user_img = forms.ImageField(widget=CustomClearableFileInput, required=False, label='')

    class Meta:
        model = User
        fields = ['nickname', 'user_img']