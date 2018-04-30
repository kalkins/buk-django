from django.conf.urls import url, include
from members import views

urlpatterns = [
    url(r'^(?P<pk>[0-9]+)$', views.MemberDetail.as_view(),
        name='member_detail'),
    url(r'^(?P<pk>[0-9]+)/endre$', views.ChangeMember.as_view(),
        name='member_change'),
    url(r'^ny$', views.AddMember.as_view(), name='member_add'),
]
