from rest_framework import serializers
from .models import Wishlist
from apps.books.serializers import BookListSerializer


class WishlistSerializer(serializers.ModelSerializer):
    books = BookListSerializer(many=True, read_only=True)

    class Meta:
        model = Wishlist
        fields = ('id', 'books', 'created_at')
