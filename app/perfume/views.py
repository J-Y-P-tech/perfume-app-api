"""
Views for the recipe APIs
"""
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from base.models import Perfume
from perfume import serializers


class PerfumeViewSet(viewsets.ModelViewSet):
    """View for manage recipe APIs."""
    serializer_class = serializers.PerfumeDetailSerializer
    queryset = Perfume.objects.all()
    # authentication_classes = (TokenAuthentication,)
    # permission_classes = (IsAuthenticated,)
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve recipes for authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        """Return the serializer class for request.
        When user is calling detail endpoint we are going to use
        RecipeDetailSerializer. For that we need to override
        get_serializer_class()
        """
        if self.action == 'list':
            # We don't return serializers.PerfumeSerializer()
            # but just serializers.PerfumeSerializer
            # this method do not require instance of a class
            # just reference
            return serializers.PerfumeSerializer

        # If action is not list we will return RecipeDetailSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new perfume."""
        serializer.save(user=self.request.user)
