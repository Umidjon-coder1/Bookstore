from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
from apps.books.models import Book


class CartAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_cart(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user, defaults={'session_key': ''})
        return cart

    def get(self, request):
        cart = self.get_cart(request)
        return Response(CartSerializer(cart).data)

    def delete(self, request):
        cart = self.get_cart(request)
        cart.items.all().delete()
        return Response({'detail': 'Cart cleared.'})


class CartItemAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        book_id = request.data.get('book_id')
        quantity = int(request.data.get('quantity', 1))
        book = Book.objects.filter(pk=book_id, is_active=True).first()
        if not book:
            return Response({'error': 'Book not found.'}, status=status.HTTP_404_NOT_FOUND)
        cart, _ = Cart.objects.get_or_create(user=request.user, defaults={'session_key': ''})
        item, created = CartItem.objects.get_or_create(cart=cart, book=book)
        item.quantity = item.quantity + quantity if not created else quantity
        item.save()
        return Response(CartSerializer(cart).data)

    def patch(self, request, item_id):
        item = CartItem.objects.filter(pk=item_id, cart__user=request.user).first()
        if not item:
            return Response({'error': 'Item not found.'}, status=status.HTTP_404_NOT_FOUND)
        quantity = int(request.data.get('quantity', 1))
        if quantity > 0:
            item.quantity = quantity
            item.save()
        else:
            item.delete()
        return Response(CartSerializer(item.cart).data)

    def delete(self, request, item_id):
        item = CartItem.objects.filter(pk=item_id, cart__user=request.user).first()
        if not item:
            return Response({'error': 'Item not found.'}, status=status.HTTP_404_NOT_FOUND)
        cart = item.cart
        item.delete()
        return Response(CartSerializer(cart).data)
