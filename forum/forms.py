from django.forms import ModelForm

from base.forms import BaseCommentForm

from .models import Post, ForumComment


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'content', 'forum')


class ForumCommentForm(BaseCommentForm):
    class Meta(BaseCommentForm.Meta):
        model = ForumComment
