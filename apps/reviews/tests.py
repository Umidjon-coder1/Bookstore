from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.books.models import Book, Author, Category
from .models import Review

User = get_user_model()


class ReviewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='reviewer', email='reviewer@example.com', password='pass')
        self.author = Author.objects.create(name='Rev Author', slug='rev-author')
        self.cat = Category.objects.create(name='Rev Cat', slug='rev-cat')
        self.book = Book.objects.create(title='Rev Book', slug='rev-book', author=self.author, category=self.cat, price=10, quantity=5, isbn='4444444444444')

    def test_review_updates_book_rating(self):
        Review.objects.create(book=self.book, user=self.user, rating=4, body='Good')
        self.book.refresh_from_db()
        self.assertEqual(self.book.rating, 4.0)
