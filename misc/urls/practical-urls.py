from django.conf.urls import url, include
from misc import views

urlpatterns = [
    url(r'^$', views.Practical.as_view(), name='practical'),
]
