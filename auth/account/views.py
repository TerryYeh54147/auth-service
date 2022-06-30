import datetime as dt
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
        msg['msg'] = f'KeyError: username and password are required.'
        return JsonResponse(msg, status=status.HTTP_400_BAD_REQUEST)
    auth = Auth(request)
    if auth.login(username, password):
        msg = auth.token
        msg['msg'] = 'Login successful.'
        status_code = status.HTTP_200_OK
    else:
        msg['msg'] = "Invalid username or password."
        status_code = status.HTTP_401_UNAUTHORIZED

    return JsonResponse(msg, status=status_code)


@swagger_auto_schema(
    methods=['GET'],
    operation_summary='Get system user list',
    operation_description='Accept pass any params belong Account model, and only filter datetime instances that match date.'
)
@api_view(http_method_names=['GET'])
def get_users(request):
    """
    Get accounts' data and order by id
    Default get all accounts' data
    Accept pass any params belong Account model, and its element can be multiple except the datetime field 
    For datetime fields, only filter datetime instances that matches date or null
    """
    users = Account.objects.all().order_by('id')
    # print(f'request data: {request.GET}')
    # print(f'request keys: {request.GET.keys()}')
    params_key = request.GET.keys()
    args = {}
    fields_name = [a.name for a in Account._meta.get_fields()]
    # print(f'account fields: {fields_name}')
    for key in params_key:
        # skip wrong params that is not in Account fields
        if key not in fields_name:
            return JsonResponse({'msg': f'Params key {key} not found in Account fields.'}, safe=False, status=status.HTTP_404_NOT_FOUND)
        else:
            field_type = Account._meta.get_field(key).get_internal_type()
            # print(f'{key} field type: {field_type}')
            # Unsupported lookup '' for UUIDField or join on the field not permitted
            if field_type == 'UUIDField':
                return JsonResponse({'msg': f'Params key unsupported lookup for {field_type} or join on the field not permitted'}, safe=False, status=status.HTTP_400_BAD_REQUEST)
            filter_key = f'{key}__'
            is_datetime_type =  field_type == 'DateTimeField'
            val_split_char = '-' if is_datetime_type else ','
            filter_val = request.GET.get(key)
            filter_vals = filter_val.split(val_split_char)
            if is_datetime_type:
                filter_vals = True if filter_vals[0] == 'null' else dt.date(*list(map(int, filter_vals[:3])))
            if is_datetime_type:
                filter_key += 'isnull' if filter_vals is True else 'contains'
            args[filter_key] = filter_vals
    print(f'args: {args}')
    users = users.filter(**args)
    acounts_serializer = AccountSerializer(users, many=True)
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
        return JsonResponse({'msg': f'KeyError: {cur_field} not found'}, safe=False, status=status.HTTP_400_BAD_REQUEST)
    username = request.data['username']
    if Account.objects.filter(username=username):
        return JsonResponse({'msg': f"duplicate username: {username}"}, safe=False, status=status.HTTP_409_CONFLICT)
    role = request.data['role']
    if role not in dict(Account.ROLES).keys():
        return JsonResponse({'msg': f"Role: {role} not found"}, safe=False, status=status.HTTP_400_BAD_REQUEST)
    query_data = {k: request.data.get(
        k) for k in filled_data['required']+filled_data['nullable']}
    pwd = query_data['password']
    validate_pwd_error = Auth(request).validate_pwd(pwd=pwd)
    if len(validate_pwd_error):
        err_msg = '/'.join(validate_pwd_error)
        return JsonResponse({'msg': err_msg}, safe=False, status=status.HTTP_400_BAD_REQUEST)
    user = Account.objects.create_user(**query_data)
    user_serializer = AccountSerializer(user)
    return JsonResponse(user_serializer.data, safe=False, status=status.HTTP_201_CREATED)
