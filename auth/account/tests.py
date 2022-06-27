import random

from django.test import TestCase
from rest_framework import status

from .models import Account


# Create your tests here.
class AccountTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_data = {
            'username': 'testuser',
            'password': 'pwd1357',
            'role': 'owner',
            'email': 'testuser@example.com',
            'phone': '0123456789',
            'first_name': 'user',
            'last_name': 'test',
        }
        cls.new_user=Account.objects.create_user(**cls.user_data)
        cls.urls = {
            'api_host': '/api/user/',
            'login': 'login/',
            'create': 'add/',
        }
        cls.rand_seed = 10

    def get_login_token(self):
        url = self.urls['api_host'] + self.urls['login']
        login_data = {'username':self.user_data['username'], 'password':self.user_data['password']}
        response = self.client.post(url, data=login_data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token = response.json()['access']
        return f'Bear {token}'

    def create_account(self, data=None):
        url = self.urls['api_host'] + self.urls['create']
        header = self.get_login_token()
        return self.client.post(url, data, content_type='application/json', HTTP_AUTHORIZATION=header)

    '''
    # TODO: solve this duplicate key issue
    def test_create_account_success(self):
        data = self.user_data.copy()
        data['username'] = 'testuser2'
        data['first_name'] = 'user2'
        response = self.create_account(data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    '''

    def test_create_account_duplicate(self):
        duplicate_username = self.user_data['username']
        # print(f'\n>>>[testing] duplicate username: {duplicate_username}')
        msg = f"duplicate username: {duplicate_username}"
        response = self.create_account(self.user_data)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.json()['ErrorMsg'], msg)

    def test_create_account_losing_critical_key(self):
        critical_keys = ['username', 'password', 'role']
        target_key = critical_keys[random.randint(0, len(critical_keys) - 1)]
        # print(f'\n>>>[testing] losing target_key: {target_key}')
        msg = f'KeyError: {target_key} not found'
        data = self.user_data.copy()
        del data[target_key]
        response = self.create_account(data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()['ErrorMsg'], msg)
    