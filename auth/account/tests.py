import random

from django.test import TestCase
from django.conf import settings
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
        cls.urls = {
            'api_host': '/api/user/',
            'login': 'login/',
            'create': 'add/',
        }
        cls.rand_seed = 10

    def setUp(self):
        self.new_user = Account.objects.create_user(**self.user_data)

    def login_account(self, username, password):
        url = self.urls['api_host'] + self.urls['login']
        login_data = {'username': username, 'password': password}
        response = self.client.post(
            url, data=login_data, content_type='application/json')
        return response

    def get_login_token(self):
        login_data = {
            'username': self.user_data['username'], 'password': self.user_data['password']}
        response = self.login_account(**login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token = response.json()['access']
        return f'Bear {token}'

    def test_login_access(self):
        msg = 'Login successful.'
        login_data = {
            'username': self.user_data['username'], 'password': self.user_data['password']}
        response = self.login_account(**login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['msg'], msg)

    def test_login_invalid_username(self):
        msg = 'Invalid username or password.'
        wrong_username='invalid_username'
        login_data = {
            'username': wrong_username, 'password': self.user_data['password']}
        response = self.login_account(**login_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json()['msg'], msg)

    def test_login_invalid_password(self):
        msg = 'Invalid username or password.'
        wrong_password='invalid_username'
        login_data = {
            'username': self.user_data['username'], 'password': wrong_password}
        response = self.login_account(**login_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json()['msg'], msg)

    def create_account(self, data=None):
        url = self.urls['api_host'] + self.urls['create']
        header = self.get_login_token()
        return self.client.post(url, data, content_type='application/json', HTTP_AUTHORIZATION=header)

    def test_create_account_success(self):
        data = self.user_data.copy()
        data['username'] = 'testuser2'
        data['first_name'] = 'user2'
        response = self.create_account(data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_account_duplicate(self):
        duplicate_username = self.user_data['username']
        # print(f'\n>>>[testing] duplicate username: {duplicate_username}')
        msg = f"duplicate username: {duplicate_username}"
        response = self.create_account(self.user_data)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.json()['msg'], msg)

    def test_create_account_losing_critical_key(self):
        critical_keys = ['username', 'password', 'role']
        target_key = critical_keys[random.randint(0, len(critical_keys) - 1)]
        # print(f'\n>>>[testing] losing target_key: {target_key}')
        msg = f'KeyError: {target_key} not found'
        data = self.user_data.copy()
        del data[target_key]
        response = self.create_account(data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()['msg'], msg)

    def test_create_account_wrong_role_option(self):
        wrong_role = 'maintainers'
        msg = f'Role: {wrong_role} not found'
        data = self.user_data.copy()
        data['username'] = 'testRole'
        data['role'] = wrong_role
        response = self.create_account(data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()['msg'], msg)

    def test_create_account_less_than_min_password(self, password='pwd'):
        min_length = [validator for validator in settings.AUTH_PASSWORD_VALIDATORS if 'MinimumLengthValidator' in validator['NAME']][0].get(
            'OPTIONS').get('min_length')
        username = f'less_{min_length}_pwd'
        msg = f'這個密碼過短。請至少使用 {min_length} 個字元。'
        data = self.user_data.copy()
        data['username'] = username
        data['password'] = password
        response = self.create_account(data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()['msg'], msg)

    def test_create_account_empty_password(self):
        self.test_create_account_less_than_min_password(password='')

    def test_create_account_common_password(self):
        common_pwd = 'test1234'
        msg = '這個密碼太普通。'
        data = self.user_data.copy()
        data['username'] = common_pwd
        data['password'] = common_pwd
        response = self.create_account(data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()['msg'], msg)

    ''' 
    # TODO: check how to handle the similar case(UserAttributeSimilarityValidator)
    def test_create_account_similar_password(self):
        username, similar_pwd = 'similar_pwd', 'similar_pwd'
        msg = f'這個密碼與使用者名稱太相近。'
        data = self.user_data.copy()
        data['username'] = username
        data['password'] = similar_pwd
        response = self.create_account(data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()['msg'], msg)
    '''

    def test_create_account_only_number_password(self):
        # 這個密碼只包含數字。
        username = f'only_number_password'
        msg = f'這個密碼只包含數字。'
        data = self.user_data.copy()
        data['username'] = username
        data['password'] = '2840184892'
        response = self.create_account(data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()['msg'], msg)
