from django.urls import path
from . import api_views

app_name = 'api-orders'

urlpatterns = [
    path('', api_views.OrderListCreateAPIView.as_view(), name='list-create'),
    path('addresses/', api_views.AddressListCreateAPIView.as_view(), name='addresses'),
    path('<str:order_number>/', api_views.OrderDetailAPIView.as_view(), name='detail'),
]
