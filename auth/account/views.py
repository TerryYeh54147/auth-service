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
