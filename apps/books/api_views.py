from rest_framework import generics, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from .models import Book, Category, Author
from .serializers import BookListSerializer, BookDetailSerializer, BookWriteSerializer, CategorySerializer, AuthorSerializer
from .filters import BookFilter
from apps.users.permissions import IsStoreManager


class BookListCreateView(generics.ListCreateAPIView):
    queryset = Book.objects.filter(is_active=True).select_related('author', 'category')
    filterset_class = BookFilter
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'author__name', 'isbn', 'description']
    ordering_fields = ['price', 'rating', 'created_at', 'title']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return BookWriteSerializer
        return BookListSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsStoreManager()]
        return [AllowAny()]


class BookRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Book.objects.filter(is_active=True)
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return BookWriteSerializer
        return BookDetailSerializer

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsStoreManager()]
        return [AllowAny()]


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]


class AuthorListView(generics.ListAPIView):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class FeaturedBooksView(generics.ListAPIView):
    queryset = Book.objects.filter(is_active=True, is_featured=True).select_related('author', 'category')
    serializer_class = BookListSerializer
    permission_classes = [AllowAny]
