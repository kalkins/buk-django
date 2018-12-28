from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.list import ListView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse

from utils.views import MultiFormView
from polls.views import PollCreateFormView, PollAnswerFormView

from .models import Post
from .forms import PostForm, ForumCommentForm


class UserCanAccessForumMixin(UserPassesTestMixin):
    def test_func(self, *args, **kwargs):
        user = self.request.user

        if not user.is_authenticated:
            return False

        kwargs = self.request.resolver_match.kwargs

        # If there is no forum specified in the URL, it is optional
        # and we allow access
        if 'forum' not in kwargs:
            return True

        for forum in Post.FORUM_CHOICES:
            if forum[0] == kwargs['forum']:
                if 'pk' in kwargs:
                    post = get_object_or_404(Post, pk=kwargs['pk'])
                    if post.forum != forum[0]:
                        raise Http404("Ugyldig URL")

                if Post.user_can_access_forum(user, forum[0]):
                    return True

        raise Http404("Du har ikke tilgang til dette forumet")


class PostForm(MultiFormView):
    batch = True
    forms = [
        {'name': 'post_form', 'form': PostForm},
    ]

    def save_post_form(self, form):
        post = form.save(commit=False)
        post.poster = self.request.user
        if 'poll_form' in self.form_instances:
            post.poll = self.form_instances['poll_form'].instance
        post.save()
        self.success_url = post.get_absolute_url()


class PostCreate(UserCanAccessForumMixin, PollCreateFormView, PostForm):
    template_name = 'forum/post_create.html'

    def get_post_form_initial(self):
        return {'forum': self.kwargs['forum']}


class PostUpdate(UserCanAccessForumMixin, SingleObjectMixin, PollCreateFormView, PostForm):
    model = Post
    template_name = 'forum/post_update.html'

    def get_post_form_instance(self):
        return self.get_object()

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        return super().get_context_data(**kwargs)


class PostDetail(UserCanAccessForumMixin, PollAnswerFormView):
    model = Post
    context_object_name = 'post'
    forms = [
        {'name': 'comment_form', 'form': ForumCommentForm},
    ]
    template_name = 'forum/post_detail.html'

    def save_comment_form(self, form):
        comment = form.save(commit=False)
        comment.post = self.get_object()
        comment.poster = self.request.user
        comment.save()

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        context = super().get_context_data(**kwargs)
        prev = self.request.GET.get('prev')
        if prev:
            context['back_link'] = reverse(prev)
        else:
            forum_link = reverse('forum_post_list', args=[self.kwargs['forum']])
            context['back_link'] = forum_link
        return context


class PostList(UserCanAccessForumMixin, ListView):
    model = Post
    context_object_name = 'posts'

    def get_queryset(self):
        kwargs = self.request.resolver_match.kwargs
        self.forum = kwargs['forum'] if 'forum' in kwargs else Post.VARIOUS
        return Post.objects.filter(forum=self.forum).prefetch_related('poster')

    def get_context_data(self, *args, **kwargs):
        context = super(PostList, self).get_context_data(*args, **kwargs)

        for forum in Post.FORUM_CHOICES:
            if forum[0] == self.forum:
                context['forum_name'] = forum[1]
                break

        context['forums'] = Post.FORUM_CHOICES
        context['new_post_url'] = reverse('forum_post_create', args=[self.kwargs['forum']])

        return context


class AllPostList(UserCanAccessForumMixin, ListView):
    model = Post
    context_object_name = 'posts'
    template_name = 'forum/all_post_list.html'

    def get_queryset(self):
        return Post.objects.all().prefetch_related('poster')

    def get_context_data(self, *args, **kwargs):
        context = super(AllPostList, self).get_context_data(*args, **kwargs)

        context['forum_name'] = 'All'
        context['forums'] = Post.FORUM_CHOICES
        context['new_post_url'] = reverse('forum_post_create', args=['diverse'])

        return context
