from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.books.models import Book, Author, Category
from .models import Wishlist

User = get_user_model()


class WishlistTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='wishuser', email='wish@example.com', password='pass')
        self.author = Author.objects.create(name='A', slug='a')
        self.cat = Category.objects.create(name='C', slug='c')
        self.book = Book.objects.create(title='WB', slug='wb', author=self.author, category=self.cat, price=5, quantity=1, isbn='2222222222222')

    def test_toggle(self):
        wishlist, _ = Wishlist.objects.get_or_create(user=self.user)
        wishlist.books.add(self.book)
        self.assertIn(self.book, wishlist.books.all())
        wishlist.books.remove(self.book)
        self.assertNotIn(self.book, wishlist.books.all())
