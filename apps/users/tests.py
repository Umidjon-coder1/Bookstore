from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class UserRegistrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('users:register')

    def test_register_get(self):
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)

    def test_register_post_valid(self):
        response = self.client.post(self.register_url, {
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
        })
        self.assertTrue(User.objects.filter(email='test@example.com').exists())

    def test_register_post_duplicate_email(self):
        User.objects.create_user(username='existing', email='existing@example.com', password='pass')
        response = self.client.post(self.register_url, {
            'email': 'existing@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
        })
        self.assertEqual(response.status_code, 200)


class UserLoginTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', email='login@example.com', password='TestPass123!')
        self.login_url = reverse('users:login')

    def test_login_get(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)

    def test_login_valid(self):
        response = self.client.post(self.login_url, {'username': 'login@example.com', 'password': 'TestPass123!'})
        self.assertEqual(response.status_code, 302)

    def test_login_invalid(self):
        response = self.client.post(self.login_url, {'username': 'login@example.com', 'password': 'wrongpass'})
        self.assertEqual(response.status_code, 200)


class UserProfileTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='profiletest', email='profile@example.com', password='TestPass123!')
        self.client.login(username='profile@example.com', password='TestPass123!')

    def test_profile_get(self):
        response = self.client.get(reverse('users:profile'))
        self.assertEqual(response.status_code, 200)
