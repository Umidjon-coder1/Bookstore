from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class DashboardAccessTest(TestCase):
    def setUp(self):
        self.customer = User.objects.create_user(username='customer', email='customer@example.com', password='pass', role='customer')
        self.manager = User.objects.create_user(username='manager', email='manager@example.com', password='pass', role='store_manager')

    def test_customer_cannot_access_dashboard(self):
        self.client.login(username='customer@example.com', password='pass')
        response = self.client.get('/analytics/dashboard/')
        self.assertIn(response.status_code, [302, 403])

    def test_manager_can_access_dashboard(self):
        self.client.login(username='manager@example.com', password='pass')
        response = self.client.get('/analytics/dashboard/')
        self.assertEqual(response.status_code, 200)
