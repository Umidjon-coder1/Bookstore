from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from apps.books.models import Book, Author, Category
from .models import Cart, CartItem

User = get_user_model()


class CartTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='cartuser', email='cart@example.com', password='TestPass123!')
        self.author = Author.objects.create(name='Author', slug='author')
        self.category = Category.objects.create(name='Fiction', slug='fiction')
        self.book = Book.objects.create(title='Book', slug='book', author=self.author, category=self.category, price=10.00, quantity=5, isbn='1111111111111')

    def test_cart_page(self):
        self.client.login(username='cart@example.com', password='TestPass123!')
        response = self.client.get('/cart/')
        self.assertEqual(response.status_code, 200)

    def test_add_to_cart(self):
        self.client.login(username='cart@example.com', password='TestPass123!')
        response = self.client.post(f'/cart/add/{self.book.pk}/', {'quantity': 2})
        cart = Cart.objects.filter(user=self.user).first()
        self.assertIsNotNone(cart)
        self.assertEqual(cart.total_items, 2)
