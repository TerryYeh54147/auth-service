from rest_framework import serializers

from .models import Account


class AccountSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    def get_full_name(self, user):
        return f'{user.last_name}{user.first_name}'

    class Meta:
        model = Account
        fields = ["id", "username", "role", "email", "phone", "full_name", "last_name",
                  "first_name", "is_superuser", "date_joined", "last_edit_at", "last_login"]
