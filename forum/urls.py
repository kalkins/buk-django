from django.urls import path

from .views import PostCreate, PostUpdate, PostDetail, PostList

urlpatterns = [
    path('', PostList.as_view(), name='forum_post_list'),
    path('<forum>/', PostList.as_view(), name='forum_post_list'),
    path('<forum>/ny', PostCreate.as_view(), name='forum_post_create'),
    path('<forum>/<int:pk>', PostDetail.as_view(),
         name='forum_post_detail'),
    path('<forum>/<int:pk>/endre', PostUpdate.as_view(),
         name='forum_post_update'),
]
