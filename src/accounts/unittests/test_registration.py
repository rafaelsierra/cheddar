from django.contrib.auth.models import User
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

class RegistrationTestCase(APITestCase):
    def setUp(self):
        self.url = '/v1/account'
        self.user = User(username='sdm', is_active=True)
        self.user.set_password('1234')
        self.user.save()

    def test_anonymous_user_trying_to_GET(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)

    def test_authenticated_user_trying_to_POST(self):
        self.client.login(username='sdm', password='1234')
        response = self.client.post(
            self.url,
            {
                'username': 'foo',
                'password': 'bar',
                'email': 'foo@bar.xxx'
            }
        )
        self.assertEqual(response.status_code, 403)

    def test_authenticated_user_trying_to_GET(self):
        self.client.login(username='sdm', password='1234')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['username'], 'sdm')
        self.assertListEqual(
            list(response.data.keys()),
            ['username', 'email', 'first_name', 'last_name', 'last_login', 'date_joined']
        )

    def test_anonymous_user_trying_to_register(self):
        response = self.client.post(
            self.url,
            {
                'username': 'foo',
                'password': 'bar',
                'email': 'foo@bar.xxx'
            }
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['username'], 'foo')
        self.assertEqual(response.data['email'], 'foo@bar.xxx')
        self.assertListEqual(
            list(response.data.keys()),
            ['username', 'email', 'first_name', 'last_name', 'last_login', 'date_joined']
        )

