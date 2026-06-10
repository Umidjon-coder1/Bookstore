import django_filters
from .models import Book, Category, Author


class BookFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    category = django_filters.CharFilter(field_name='category__slug')
    author = django_filters.CharFilter(field_name='author__slug')
    min_rating = django_filters.NumberFilter(field_name='rating', lookup_expr='gte')
    in_stock = django_filters.BooleanFilter(method='filter_in_stock')
    on_sale = django_filters.BooleanFilter(method='filter_on_sale')
    language = django_filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = Book
        fields = ['category', 'author', 'language', 'stock_status', 'is_featured']

    def filter_in_stock(self, queryset, name, value):
        if value:
            return queryset.exclude(stock_status='out_of_stock')
        return queryset

    def filter_on_sale(self, queryset, name, value):
        if value:
            return queryset.filter(discount_price__isnull=False)
        return queryset
