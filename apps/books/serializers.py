from rest_framework import serializers
from .models import Book, Category, Author, Publisher, BookImage


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'description', 'image', 'parent')


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ('id', 'name', 'slug', 'bio', 'photo')


class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = ('id', 'name', 'website', 'address')


class BookImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookImage
        fields = ('id', 'image', 'alt_text', 'order')


class BookListSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    final_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    is_on_sale = serializers.BooleanField(read_only=True)
    discount_percentage = serializers.IntegerField(read_only=True)

    class Meta:
        model = Book
        fields = ('id', 'title', 'slug', 'author_name', 'category_name', 'price', 'discount_price', 'final_price', 'is_on_sale', 'discount_percentage', 'cover_image', 'rating', 'reviews_count', 'stock_status', 'is_featured')


class BookDetailSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    publisher = PublisherSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    images = BookImageSerializer(many=True, read_only=True)
    final_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    is_on_sale = serializers.BooleanField(read_only=True)
    discount_percentage = serializers.IntegerField(read_only=True)

    class Meta:
        model = Book
        fields = '__all__'


class BookWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        exclude = ('rating', 'reviews_count', 'created_at', 'updated_at')
