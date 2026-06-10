from django.urls import path
from . import api_views

app_name = 'api-cart'

urlpatterns = [
    path('', api_views.CartAPIView.as_view(), name='cart'),
    path('items/', api_views.CartItemAPIView.as_view(), name='items'),
    path('items/<int:item_id>/', api_views.CartItemAPIView.as_view(), name='item-detail'),
]
