from django.http import Http404
from django.views import View
from django.shortcuts import get_object_or_404
from django.views.generic.edit import CreateView, UpdateView, FormMixin
from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import UserPassesTestMixin

from polls.views import PollFormMixin

from .models import Post
from .forms import CommentForm


class UserCanAccessForumMixin(UserPassesTestMixin):
    def test_func(self, *args, **kwargs):
        user = self.request.user

        if not user.is_authenticated():
            return False

        kwargs = self.request.resolver_match.kwargs
        for forum in Post.FORUM_SHORTNAME:
            if forum[1] == kwargs['forum']:
                if 'pk' in kwargs:
                    post = get_object_or_404(Post, pk=kwargs['pk'])
                    if post.forum != forum[0]:
                        break

                if Post.user_can_access_forum(user, forum[0]):
                    return True

        raise Http404


class ForumEditingMixin(FormMixin):
    def get_form(self, *args, **kwargs):
        form = super(ForumEditingMixin, self).get_form(*args, **kwargs)
        form.fields['forum'].choices = Post.available_forums(self.request.user)
        return form

    def get_initial(self, *args, **kwargs):
        initial = super(ForumEditingMixin, self).get_initial(*args, **kwargs)

        forum_short = self.request.resolver_match.kwargs['forum']

        for forum in Post.FORUM_SHORTNAME:
            if forum[1] == forum_short:
                initial['forum'] = forum[0]
                break

        return initial

    def form_valid(self, form):
        form.instance.poster = self.request.user
        return super(ForumEditingMixin, self).form_valid(form)


class PostCreate(UserCanAccessForumMixin, ForumEditingMixin, PollFormMixin, CreateView):
    model = Post
    fields = ('title', 'content', 'forum')
    template_name_suffix = '_create'


class PostUpdate(UserCanAccessForumMixin, ForumEditingMixin, PollFormMixin, UpdateView):
    model = Post
    fields = ('title', 'content', 'forum')
    template_name_suffix = '_update'


class PostDisplay(DetailView):
    model = Post
    context_object_name = 'post'

    def get_context_data(self, *args, **kwargs):
        context = super(PostDisplay, self).get_context_data(*args, **kwargs)
        context['comment_form'] = CommentForm(initial={
                                                'post': self.object,
                                                'poster': self.request.user})
        return context


class PostComment(CreateView):
    form_class = CommentForm
    template_name = 'forum/post_detail.html'
    context_object_name = 'comment_form'

    def get_context_data(self, *args, **kwargs):
        context = super(PostDisplay, self).get_context_data(*args, **kwargs)
        pk = self.request.resolver_match.kwargs['pk']
        context['post'] = get_object_or_404(Post, pk=pk)


class PostDetail(UserCanAccessForumMixin, View):
    def get(self, *args, **kwargs):
        view = PostDisplay.as_view()
        return view(*args, **kwargs)

    def post(self, *args, **kwargs):
        view = PostComment.as_view()
        return view(*args, **kwargs)
