from django.contrib.auth.models import User
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import ValidationError


class CustomAuthentication(JWTAuthentication):
    SUPER_SIGNATURE = 'super_user_token'

    def authenticate(self, request):
        try:
            user, validated_token = super(CustomAuthentication, self).authenticate(request)
            return user, validated_token
        except Exception as e:
            print(str(e))