from django.urls import path
from . import api_views

app_name = 'api-reviews'

urlpatterns = [
    path('', api_views.ReviewListCreateAPIView.as_view(), name='list'),
    path('<slug:book_slug>/', api_views.ReviewListCreateAPIView.as_view(), name='book-reviews'),
    path('detail/<int:pk>/', api_views.ReviewDetailAPIView.as_view(), name='detail'),
]
