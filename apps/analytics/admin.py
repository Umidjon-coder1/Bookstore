from django.contrib import admin
from .models import BookView, SalesReport


@admin.register(BookView)
class BookViewAdmin(admin.ModelAdmin):
    list_display = ('book', 'user', 'ip_address', 'viewed_at')
    list_filter = ('viewed_at',)
    search_fields = ('book__title', 'user__email')


@admin.register(SalesReport)
class SalesReportAdmin(admin.ModelAdmin):
    list_display = ('date', 'total_orders', 'total_revenue', 'total_books_sold')
