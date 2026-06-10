from django.test import TestCase, Client
from django.urls import reverse
from .models import Book, Category, Author


class BookModelTest(TestCase):
    def setUp(self):
        self.author = Author.objects.create(name='Test Author', slug='test-author')
        self.category = Category.objects.create(name='Fiction', slug='fiction')
        self.book = Book.objects.create(
            title='Test Book',
            slug='test-book',
            author=self.author,
            category=self.category,
            price=29.99,
            quantity=10,
            isbn='1234567890123',
        )

    def test_book_str(self):
        self.assertEqual(str(self.book), 'Test Book')

    def test_book_final_price_no_discount(self):
        self.assertEqual(self.book.final_price, self.book.price)

    def test_book_final_price_with_discount(self):
        self.book.discount_price = 19.99
        self.book.save()
        self.assertEqual(self.book.final_price, self.book.discount_price)

    def test_book_stock_status_out_of_stock(self):
        self.book.quantity = 0
        self.book.save()
        self.assertEqual(self.book.stock_status, Book.StockStatus.OUT_OF_STOCK)

    def test_book_stock_status_low_stock(self):
        self.book.quantity = 3
        self.book.save()
        self.assertEqual(self.book.stock_status, Book.StockStatus.LOW_STOCK)


class BookViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.author = Author.objects.create(name='Author', slug='author')
        self.category = Category.objects.create(name='Fiction', slug='fiction')
        self.book = Book.objects.create(
            title='My Book',
            slug='my-book',
            author=self.author,
            category=self.category,
            price=15.00,
            quantity=5,
            isbn='9876543210123',
        )

    def test_book_list(self):
        response = self.client.get(reverse('books:list'))
        self.assertEqual(response.status_code, 200)

    def test_book_detail(self):
        response = self.client.get(reverse('books:detail', kwargs={'slug': 'my-book'}))
        self.assertEqual(response.status_code, 200)

    def test_search(self):
        response = self.client.get(reverse('books:search') + '?q=My')
        self.assertEqual(response.status_code, 200)
