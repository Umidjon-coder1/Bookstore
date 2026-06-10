from django.shortcuts import render, get_object_or_404
from django.views import View
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from .models import Book, Category, Author
from .filters import BookFilter


class BookListView(View):
    def get(self, request):
        queryset = Book.objects.filter(is_active=True).select_related('author', 'category')
        book_filter = BookFilter(request.GET, queryset=queryset)
        books = book_filter.qs

        # Ordering
        ordering = request.GET.get('ordering', '-created_at')
        valid_orderings = {
            'price': 'price',
            '-price': '-price',
            'title': 'title',
            '-title': '-title',
            'rating': '-rating',
            '-created_at': '-created_at',
        }
        books = books.order_by(valid_orderings.get(ordering, '-created_at'))

        paginator = Paginator(books, 12)
        try:
            page = int(request.GET.get('page', 1))
        except (ValueError, TypeError):
            page = 1
        books_page = paginator.get_page(page)

        categories = Category.objects.filter(is_active=True, parent=None).prefetch_related('children')
        authors = Author.objects.all()[:20]

        context = {
            'books': books_page,
            'categories': categories,
            'authors': authors,
            'filter': book_filter,
            'ordering': ordering,
            'total_count': book_filter.qs.count(),
        }
        return render(request, 'books/list.html', context)


class BookDetailView(View):
    def get(self, request, slug):
        book = get_object_or_404(Book, slug=slug, is_active=True)
        related_books = Book.objects.filter(
            category=book.category, is_active=True
        ).exclude(pk=book.pk)[:4]
        reviews = book.reviews.filter(is_approved=True).select_related('user')[:10]

        # Track view
        try:
            from apps.analytics.models import BookView
            BookView.objects.create(
                book=book,
                user=request.user if request.user.is_authenticated else None,
                session_key=request.session.session_key or '',
                ip_address=request.META.get('REMOTE_ADDR', ''),
            )
        except Exception:
            pass

        context = {
            'book': book,
            'related_books': related_books,
            'reviews': reviews,
            'images': book.images.all(),
        }
        return render(request, 'books/detail.html', context)


class SearchView(View):
    def get(self, request):
        query = request.GET.get('q', '').strip()
        books = Book.objects.none()
        if query:
            books = Book.objects.filter(
                Q(title__icontains=query) |
                Q(author__name__icontains=query) |
                Q(isbn__icontains=query) |
                Q(description__icontains=query),
                is_active=True
            ).select_related('author', 'category')

        paginator = Paginator(books, 12)
        page = request.GET.get('page', 1)
        books_page = paginator.get_page(page)
        categories = Category.objects.filter(is_active=True, parent=None)
        return render(request, 'books/search.html', {
            'books': books_page,
            'query': query,
            'total_count': books.count() if query else 0,
            'categories': categories,
        })


class AutocompleteView(View):
    def get(self, request):
        q = request.GET.get('q', '').strip()
        if len(q) < 2:
            return JsonResponse({'results': []})
        books = Book.objects.filter(
            Q(title__icontains=q) | Q(author__name__icontains=q),
            is_active=True
        ).select_related('author')[:8]
        results = []
        for b in books:
            results.append({
                'title': b.title,
                'author': b.author.name if b.author else '',
                'url': b.get_absolute_url(),
                'price': str(b.final_price),
                'cover': b.cover_image.url if b.cover_image else '',
            })
        return JsonResponse({'results': results})
