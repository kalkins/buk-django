from django.conf.urls import url, include
from polls import views

urlpatterns = [
    url(r'^(?P<pk>[0-9]+)$', views.PollStatistics.as_view(), name='poll_statistics'),
]
