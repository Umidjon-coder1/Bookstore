from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from .models import Wishlist
from apps.books.models import Book


@method_decorator(login_required, name='dispatch')
class WishlistView(View):
    def get(self, request):
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        return render(request, 'wishlist/wishlist.html', {'wishlist': wishlist})


@method_decorator(login_required, name='dispatch')
class ToggleWishlistView(View):
    def post(self, request, book_id):
        book = get_object_or_404(Book, pk=book_id)
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        if book in wishlist.books.all():
            wishlist.books.remove(book)
            added = False
            msg = f'{book.title} istaklar ro\'yxatidan olib tashlandi.'
        else:
            wishlist.books.add(book)
            added = True
            msg = f'{book.title} istaklar ro\'yxatiga qo\'shildi!'
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'added': added, 'message': msg, 'count': wishlist.books.count()})
        messages.success(request, msg)
        return redirect('books:detail', slug=book.slug)
