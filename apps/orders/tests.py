from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.books.models import Book, Author, Category
from .models import Order, Address, OrderItem

User = get_user_model()


class OrderTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='orderuser', email='order@example.com', password='TestPass123!')
        self.author = Author.objects.create(name='A', slug='a-author')
        self.cat = Category.objects.create(name='C', slug='c-cat')
        self.book = Book.objects.create(title='Book', slug='order-book', author=self.author, category=self.cat, price=20.00, quantity=10, isbn='3333333333333')
        self.address = Address.objects.create(
            user=self.user, full_name='Test User', phone='123', address_line1='123 St',
            city='City', country='Country', postal_code='12345'
        )

    def test_order_number_generated(self):
        order = Order.objects.create(user=self.user, shipping_address=self.address, subtotal=20.00)
        self.assertTrue(order.order_number.startswith('ORD-'))

    def test_order_total_calculated(self):
        order = Order.objects.create(user=self.user, shipping_address=self.address, subtotal=20.00, shipping_cost=5.00, tax=2.00)
        self.assertEqual(order.total, 27.00)
