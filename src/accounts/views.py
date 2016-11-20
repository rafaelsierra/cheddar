from rest_framework import viewsets
from rest_framework.compat import is_authenticated
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer

from .serializers import AccountSerializer, NewAccountSerializer


class AccountViewSet(viewsets.ViewSet):
    """
    Returns current user data or create a new user when POSTing anonymously
    """
    def list(self, request, format=None):
        if not is_authenticated(request.user):
            raise NotAuthenticated()
        return Response(AccountSerializer(request.user).data)

    def create(self, request, format=None):
        if is_authenticated(request.user):
            raise PermissionDenied()

        serializer = NewAccountSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            return Response(AccountSerializer(user).data, status=201)


class AuthenticateViewSet(viewsets.ViewSet):
    """
    Creates a new Token and invalidates the old one
    """
    throttle_scope = 'login'
    serializer_class = AuthTokenSerializer

    def create(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})
