from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Wishlist
from .serializers import WishlistSerializer
from apps.books.models import Book


class WishlistAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        return Response(WishlistSerializer(wishlist).data)

    def post(self, request):
        book_id = request.data.get('book_id')
        book = Book.objects.filter(pk=book_id).first()
        if not book:
            return Response({'error': 'Book not found.'}, status=404)
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        if book in wishlist.books.all():
            wishlist.books.remove(book)
            added = False
        else:
            wishlist.books.add(book)
            added = True
        return Response({'added': added, 'count': wishlist.books.count()})
