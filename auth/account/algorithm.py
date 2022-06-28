from django.contrib import auth
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken


class Auth:
    def __init__(self, request):
        self.request = request
        self.user = None
        self.token = None
        self.auth_response = None

    # simpleJwt login
    def login(self, username, password):
        self.user = auth.authenticate(username=username, password=password)
        if self.user is not None and self.user.is_active:
            auth.login(self.request, self.user)
            self._get_jwt_token()
            return True
        else:
            return False

    def _get_jwt_token(self):
        refresh = RefreshToken.for_user(self.user)
        self.token = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    # reference django.contrib.auth.password_validation.validate_password()

    def validate_pwd(self, pwd, user=None, password_validators=None):
        errors = []
        if password_validators is None:
            password_validators = auth.password_validation.get_default_password_validators()
        for validator in password_validators:
            try:
                validator.validate(pwd, user)
            except ValidationError as error:
                errors += error.messages
        return errors
