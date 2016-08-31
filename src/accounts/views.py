from rest_framework import viewsets
from rest_framework.compat import is_authenticated
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken

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


class AuthenticateView(ObtainAuthToken):
    """
    Creates a new Token and invalidates the old one
    """
    throttle_scope = 'login'
