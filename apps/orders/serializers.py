from rest_framework import serializers
from .models import Order, OrderItem, Address


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'
        read_only_fields = ('user',)


class OrderItemSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source='book.title', read_only=True)
    book_cover = serializers.ImageField(source='book.cover_image', read_only=True)

    class Meta:
        model = OrderItem
        fields = ('id', 'book', 'book_title', 'book_cover', 'quantity', 'price', 'total')


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    shipping_address = AddressSerializer(read_only=True)

    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ('order_number', 'user', 'total', 'created_at', 'updated_at')
