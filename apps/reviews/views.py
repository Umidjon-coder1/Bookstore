from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views import View
from django.utils.decorators import method_decorator
from .models import Review
from apps.books.models import Book


@method_decorator(login_required, name='dispatch')
class AddReviewView(View):
    def post(self, request, book_slug):
        book = get_object_or_404(Book, slug=book_slug)
        rating = request.POST.get('rating')
        title = request.POST.get('title', '')
        body = request.POST.get('body', '')

        if not rating or not body:
            messages.error(request, 'Reyting va sharh matni majburiy.')
            return redirect('books:detail', slug=book_slug)

        review, created = Review.objects.get_or_create(
            book=book, user=request.user,
            defaults={'rating': rating, 'title': title, 'body': body}
        )
        if not created:
            review.rating = rating
            review.title = title
            review.body = body
            review.save()
            messages.success(request, 'Sharh yangilandi!')
        else:
            messages.success(request, 'Sharh yuborildi!')
        return redirect('books:detail', slug=book_slug)


@method_decorator(login_required, name='dispatch')
class DeleteReviewView(View):
    def post(self, request, review_id):
        review = get_object_or_404(Review, pk=review_id, user=request.user)
        book_slug = review.book.slug
        review.delete()
        messages.success(request, 'Sharh o\'chirildi.')
        return redirect('books:detail', slug=book_slug)
