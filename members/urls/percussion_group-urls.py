from django.conf.urls import url, include
from members import views

urlpatterns = [
    url(r'^$', views.PercussionGroupList.as_view(),
        name='percussion_group_list'),
    url(r'^ny$', views.AddPercussionGroup.as_view(),
        name='percussion_group_add'),
    url(r'^(?P<pk>[0-9]+)/endre$', views.ChangePercussionGroup.as_view(),
        name='percussion_group_change'),
    url(r'^(?P<pk>[0-9]+)/slett$', views.DeletePercussionGroup.as_view(),
        name='percussion_group_delete'),
]
