from django import forms
from django.core.exceptions import ValidationError

from .models import Comment, Post
from .moderation import is_toxic


MODERATION_ERROR = (
    'Комментарий не проходит модерацию. '
    'Пожалуйста, сформулируйте мысль корректнее.'
)


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = (
            'title',
            'text',
            'pub_date',
            'category',
            'location',
            'image',
        )
        widgets = {
            'pub_date': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M',
            ),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)

    def clean_text(self):
        text = self.cleaned_data['text']
        if is_toxic(text):
            raise ValidationError(MODERATION_ERROR)
        return text
