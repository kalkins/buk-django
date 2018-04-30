from django.conf.urls import url, include
from members import views

urlpatterns = [
    url(r'^$', views.MemberList.as_view(),
        {'show_all': False}, name='member_list'),
    url(r'^alle$', views.MemberList.as_view(),
        {'show_all': True}, name='member_list_all'),
    url(r'^statistikk$', views.MemberStatistics.as_view(),
        name='member_statistics'),
]
