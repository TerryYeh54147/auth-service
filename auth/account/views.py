from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view

from .models import Account
from .serializers import AccountSerializer
from .algorithm import Auth


@swagger_auto_schema(
    methods=['POST'],
    operation_summary='login',
)
@api_view(http_method_names=['POST'])
def login(request):
    msg, status_code = {}, None
    try:
        username = request.data['username']
        password = request.data['password']
    except KeyError:
        error_msg = {"KeyError": "username and password are required."}
        return JsonResponse(error_msg, status=status.HTTP_400_BAD_REQUEST)
    auth = Auth(request)
    if auth.login(username, password):
        msg = auth.token
        msg['detail'] = 'Login successful.'
        status_code = status.HTTP_200_OK
    else:
        msg['ErrorMsg'] = "Invalid username or password."
        status_code = status.HTTP_401_UNAUTHORIZED

    return JsonResponse(msg, status=status_code)


@swagger_auto_schema(
    methods=['GET'],
    operation_summary='Get system user list',
)
@api_view(http_method_names=['GET'])
def get_all_users(request):
    """
    Get accounts' data
    """
    all_users = Account.objects.all()
    acounts_serializer = AccountSerializer(all_users, many=True)
    return JsonResponse(acounts_serializer.data, safe=False, status=status.HTTP_200_OK)


@swagger_auto_schema(
    methods=['POST'],
    operation_description='create a new user account',
)
@api_view(http_method_names=['POST'])
def create_user(request):
    """
    Create a new user account
    """
    filled_data = {'required': ['username', 'password', 'role'], 'nullable': [
        'email', 'first_name', 'last_name', 'phone']}
    cur_field = ''
    try:
        for required_field in filled_data['required']:
            cur_field = required_field
            _ = request.data[required_field]
    except KeyError:
        return JsonResponse({'ErrorMsg': f'KeyError: {cur_field} not found'}, safe=False, status=status.HTTP_400_BAD_REQUEST)
    username = request.data['username']
    if Account.objects.filter(username=username):
        return JsonResponse({'ErrorMsg': f"duplicate username: {username}"}, safe=False, status=status.HTTP_400_BAD_REQUEST)
    role = request.data['role']
    if role not in dict(Account.ROLES).keys():
        return JsonResponse({'ErrorMsg': f"Role: {role} not found"}, safe=False, status=status.HTTP_400_BAD_REQUEST)
    query_data = {k: request.data.get(
        k) for k in filled_data['required']+filled_data['nullable']}
    pwd = query_data['password']
    validate_pwd_error = Auth(request).validate_pwd(pwd=pwd)
    if len(validate_pwd_error):
        err_msg = '/'.join(validate_pwd_error)
        return JsonResponse({'ErrorMsg': err_msg}, safe=False, status=status.HTTP_400_BAD_REQUEST)
    query_data['password'] = make_password(query_data['password'])
    user = Account.objects.create(**query_data)
    user_serializer = AccountSerializer(user)
    return JsonResponse(user_serializer.data, safe=False, status=status.HTTP_200_OK)
