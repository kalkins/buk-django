from django.urls import path
from misc import views

urlpatterns = [
    path('', views.Practical.as_view(), name='practical'),
]
