from django.urls import path
from inventory import views

urlpatterns = [
    path('', views.InventoryList.as_view(), name="inventory_list"),
    path('instrument/<int:pk>/', views.InstrumentDetail.as_view(), name="instrument_detail"),
    path('jakke/<int:pk>/', views.JacketDetail.as_view(), name="jacket_detail"),
    path('bukse/<int:pk>/', views.PantsDetail.as_view(), name="pants_detail"),
    path('hatt/<int:pk>/', views.HatDetail.as_view(), name="hat_detail"),
]
