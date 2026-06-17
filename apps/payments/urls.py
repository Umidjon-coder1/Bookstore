from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('apply-coupon/', views.ApplyCouponView.as_view(), name='apply-coupon'),
    path('webhooks/stripe/', views.stripe_webhook, name='stripe-webhook'),
    path('<str:order_number>/', views.PaymentView.as_view(), name='payment'),
    path('<str:order_number>/success/', views.PaymentSuccessView.as_view(), name='success'),
]