from django.contrib import auth
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
        self.token =  {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
