from django.urls import path
from members import views

urlpatterns = [
    path('', views.MemberList.as_view(),
        {'show_all': False}, name='member_list'),
    path('alle', views.MemberList.as_view(),
        {'show_all': True}, name='member_list_all'),
    path('statistikk', views.MemberStatistics.as_view(),
        name='member_statistics'),
]
