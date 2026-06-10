from django.urls import path
from . import api_views

app_name = 'api-wishlist'

urlpatterns = [
    path('', api_views.WishlistAPIView.as_view(), name='wishlist'),
]
