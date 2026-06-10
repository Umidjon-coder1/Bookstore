from django.urls import path
from . import api_views

app_name = 'api-payments'

urlpatterns = [
    path('<str:order_number>/', api_views.PaymentAPIView.as_view(), name='payment'),
    path('coupons/apply/', api_views.ApplyCouponAPIView.as_view(), name='apply-coupon'),
]
