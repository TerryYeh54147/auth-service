from django.http import JsonResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view

from .models import Account
from .serializers import AccountSerializer


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
    acounts_serializer = AccountSerializer(all_users)
    return JsonResponse(acounts_serializer, safe=False, status_code=status.HTTP_200_OK)
