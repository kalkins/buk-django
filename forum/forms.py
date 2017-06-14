from django import forms

from .models import Comment


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('content', 'post', 'poster')
        widgets = {
            'content': forms.Textarea(attrs={'placeholder': 'Din kommentar...'}),
            'post': forms.HiddenInput(),
            'poster': forms.HiddenInput(),
        }
