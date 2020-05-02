
from django.contrib.auth import logout

from rest_framework.authentication import SessionAuthentication
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


class TokenLogin(APIView):
    serializer_class = AuthTokenSerializer

    def post(self, request, *args, **kwargs):
        # Get the user from the normal session login (non-token based)
        user = request.user

        # Create and return the token.
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})

token_login = TokenLogin.as_view()


class TokenLogout(APIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user

        # Expire all existing tokens
        for old_token in Token.objects.filter(user=user):
            old_token.delete()

        return Response(True)

token_logout = TokenLogout.as_view()


class User(APIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        response = Response({'user': user.username})
        response['User'] = user.username
        return response

user = User.as_view()
