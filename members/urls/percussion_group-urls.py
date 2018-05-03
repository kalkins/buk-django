from django.urls import path
from members import views

urlpatterns = [
    path('', views.PercussionGroupList.as_view(),
        name='percussion_group_list'),
    path('ny', views.AddPercussionGroup.as_view(),
        name='percussion_group_add'),
    path('<int:pk>/endre', views.ChangePercussionGroup.as_view(),
        name='percussion_group_change'),
    path('<int:pk>/slett', views.DeletePercussionGroup.as_view(),
        name='percussion_group_delete'),
]
