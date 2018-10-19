from django.urls import path
from members import views

urlpatterns = [
    path('<int:pk>/endre', views.ChangeCommittee.as_view(), name='change_committee'),
]
