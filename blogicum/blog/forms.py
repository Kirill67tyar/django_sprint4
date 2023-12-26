from django import forms
from django.contrib.auth import get_user_model

from blog.models import (
    Post,
    Comment,
)

User = get_user_model()


class UserModelForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'username',
            'email',
        )


class PostModelForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = '__all__'
        exclude = 'author',  # 'location', 'category',
        widgets = {
            'pub_date': forms.DateInput(attrs={'type': 'date', }),
        }


class CommentModelForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
