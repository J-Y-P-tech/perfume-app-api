"""
Views for the user API.
"""
from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from user.serializers import (
    UserSerializer,
    AuthTokenSerializer,
)


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system.
    The CreateAPIView handles an HTTP POST request that's
    designed for creating objects. So it creates objects in the
    database. It handles all of that logic for us.
    """
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user.

    CreateTokenView that inherits from ObtainAuthToken. This view is designed to handle a
    POST request containing a user's credentials (username and password) and create a new
    authentication token for that user.
    The AuthTokenSerializer is specified as the serializer class to be used to validate the user's
    credentials and generate the authentication token. This serializer is responsible for validating
    the user's input data and serializing the token data to be sent back to the user.
    The renderer_classes attribute specifies the rendering classes that should be used to
    format the response data. The api_settings.DEFAULT_RENDERER_CLASSES is a default list of
    renderer classes defined by Django REST framework that includes JSONRenderer,
    BrowsableAPIRenderer, and AdminRenderer.
    When a user sends a POST request to the CreateTokenView endpoint with valid credentials,
    the view will authenticate the user and generate a new token. The token data will then be
    serialized using the AuthTokenSerializer and returned to the user in the specified format,
    which in this case would be JSON, HTML or Admin interface.
    """
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user."""
    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Retrieve and return the authenticated user."""
        return self.request.user
