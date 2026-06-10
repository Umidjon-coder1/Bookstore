from django.contrib import admin
from .models import Category, Author, Publisher, Book, BookImage


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'is_active', 'created_at')
    list_filter = ('is_active', 'parent')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ('name', 'website')
    search_fields = ('name',)


class BookImageInline(admin.TabularInline):
    model = BookImage
    extra = 1
    fields = ('image', 'alt_text', 'order')


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'price', 'discount_price', 'stock_status', 'quantity', 'is_active', 'is_featured', 'rating')
    list_filter = ('is_active', 'is_featured', 'stock_status', 'category', 'language')
    search_fields = ('title', 'isbn', 'author__name')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at', 'rating', 'reviews_count')
    list_editable = ('is_active', 'is_featured', 'price')
    inlines = [BookImageInline]
    fieldsets = (
        ('Basic Info', {'fields': ('title', 'slug', 'isbn', 'author', 'publisher', 'category', 'language')}),
        ('Content', {'fields': ('description', 'cover_image', 'publication_date', 'pages')}),
        ('Pricing', {'fields': ('price', 'discount_price')}),
        ('Inventory', {'fields': ('quantity', 'stock_status')}),
        ('Status', {'fields': ('is_active', 'is_featured')}),
        ('Stats', {'fields': ('rating', 'reviews_count', 'created_at', 'updated_at')}),
    )
