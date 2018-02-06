from django.conf.urls import url

from .views import PostCreate, PostUpdate, PostDetail

urlpatterns = [
    url(r'^(?P<forum>[a-zA-Z]+)/ny', PostCreate.as_view(), name='forum_post_create'),
    url(r'^(?P<forum>[a-zA-Z]+)/(?P<pk>[0-9]+)$', PostDetail.as_view(),
        name='forum_post_detail'),
    url(r'^(?P<forum>[a-zA-Z]+)/(?P<pk>[0-9]+)/endre$', PostUpdate.as_view(),
        name='forum_post_update'),
]
