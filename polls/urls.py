from django.urls import path
from polls import views

urlpatterns = [
    path('<int:pk>', views.PollStatistics.as_view(), name='poll_statistics'),
]
