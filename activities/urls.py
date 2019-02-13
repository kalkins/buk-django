from django.urls import path

from .views import (CreateActivity, UpdateActivity, DeleteActivity,
                    ActivityDetailView, ActivityListView)

urlpatterns = [
    path('', ActivityListView.as_view(), name='activity_list'),
    path('ny/', CreateActivity.as_view(), name='activity_create'),
    path('<int:pk>', ActivityDetailView.as_view(), name='activity_detail'),
    path('<int:pk>/endre', UpdateActivity.as_view(), name='activity_update'),
    path('<int:pk>/slett', DeleteActivity.as_view(), name='activity_delete'),
]
