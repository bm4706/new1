from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': '제목을 입력해주세요'}),
            'content': forms.Textarea(attrs={'placeholder': '내용을 입력해주세요'}),
        }
