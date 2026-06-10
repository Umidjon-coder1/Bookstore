from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from .models import Coupon

User = get_user_model()


class CouponTest(TestCase):
    def setUp(self):
        self.coupon = Coupon.objects.create(
            code='TEST10',
            discount_type='percentage',
            discount_value=10,
            min_order_amount=0,
            max_uses=100,
            valid_from=timezone.now() - timedelta(days=1),
            valid_until=timezone.now() + timedelta(days=30),
            is_active=True,
        )

    def test_coupon_is_valid(self):
        self.assertTrue(self.coupon.is_valid())

    def test_coupon_discount_percentage(self):
        discount = self.coupon.get_discount_amount(100)
        self.assertEqual(discount, 10)

    def test_expired_coupon(self):
        self.coupon.valid_until = timezone.now() - timedelta(days=1)
        self.coupon.save()
        self.assertFalse(self.coupon.is_valid())
