from django.urls import path
from members import views

urlpatterns = [
    path('<int:pk>', views.MemberDetail.as_view(),
        name='member_detail'),
    path('<int:pk>/endre', views.ChangeMember.as_view(),
        name='member_change'),
    path('ny', views.AddMember.as_view(), name='member_add'),
]
