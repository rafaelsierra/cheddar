from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase


class AuthenticationTestCase(APITestCase):
    def setUp(self):
        self.url = '/v1/obtain-auth-token'
        self.user = User(username='sdm', is_active=True)
        self.user.set_password('1234')
        self.user.save()

    def tearDown(self):
        self.user.delete()

    def test_obtain_auth_token(self):
        response = self.client.post(
            self.url,
            {
                'username': self.user.username,
                'password': '1234',
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.data)

    def test_use_token(self):
        token = Token.objects.get_or_create(user=self.user)[0]
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(token.key))
        response = self.client.get('/v1/account')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['username'], self.user.username)
        token.delete()

    def test_destroy_token(self):
        token = Token.objects.get_or_create(user=self.user)[0]
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(token.key))
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(len(response.content), 0)
        self.assertFalse(Token.objects.filter(user=self.user).exists())

    def test_destroy_token_without_token(self):
        response = self.client.delete(self.url, status=401)
        self.assertEqual(response.status_code, 401)
        self.assertFalse(Token.objects.filter(user=self.user).exists())
