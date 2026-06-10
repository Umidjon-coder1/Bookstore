from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Order, Address
from .serializers import OrderSerializer, AddressSerializer
from apps.users.permissions import IsStoreManager


class OrderListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_super_admin or self.request.user.is_store_manager:
            return Order.objects.all().select_related('user', 'shipping_address')
        return Order.objects.filter(user=self.request.user).select_related('shipping_address')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class OrderDetailAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'order_number'

    def get_queryset(self):
        if self.request.user.is_super_admin or self.request.user.is_store_manager:
            return Order.objects.all()
        return Order.objects.filter(user=self.request.user)


class AddressListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
