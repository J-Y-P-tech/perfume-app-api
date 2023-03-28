"""
Views for the recipe APIs
"""
from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from base.models import Perfume, Designer, Note
from perfume import serializers

from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)

"""
We're using the extend schema view, which is the decorator that allows us 
to extend the auto generated schema that's created by Django rest spectacular.
"""


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter('designers',
                             OpenApiTypes.STR,
                             description='Coma separated list of designer IDs to filter.'
                             ),
            OpenApiParameter('notes',
                             OpenApiTypes.STR,
                             description='Coma separated list of notes IDs to filter.'
                             ),
        ]
    )
)
class PerfumeViewSet(viewsets.ModelViewSet):
    """View for manage perfume APIs."""
    serializer_class = serializers.PerfumeDetailSerializer
    queryset = Perfume.objects.all()
    # authentication_classes = (TokenAuthentication,)
    # permission_classes = (IsAuthenticated,)
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def _params_to_ints(self, qs):
        """Convert a list of strings to integers."""
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        """Retrieve perfumes for authenticated user."""
        designers = self.request.query_params.get('designers')
        notes = self.request.query_params.get('notes')
        queryset = self.queryset
        if designers:
            designer_ids = self._params_to_ints(designers)
            queryset = queryset.filter(designers__id__in=designer_ids)
        if notes:
            notes_ids = self._params_to_ints(notes)
            queryset = queryset.filter(notes__id__in=notes_ids)

        return queryset.filter(
            user=self.request.user
        ).order_by('-id').distinct()

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
        elif self.action == 'upload_image':
            return serializers.PerfumeImageSerializer

        # If action is not list we will return RecipeDetailSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new perfume."""
        serializer.save(user=self.request.user)

    """
    Here we add custom action using @action decorator provided
    by Django Rest Framework.
    The actions decorator lets you specify the different HTTP methods 
    that are supported by the custom action.
    methods=['POST'] means that we accept only POST actions.
    detail=True --> this is applicable to detailviewset only not listviewset
    url_path='upload-image' --> custom url path connected to
    reverse('perfume:perfume-upload-image', args=[perfume_id])    
    """

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an image to perfume."""
        perfume = self.get_object()
        serializer = self.get_serializer(perfume, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter('assigned_only',
                             OpenApiTypes.INT, enum=[0, 1],
                             description='Filter by items assigned to perfumes.'
                             ),
        ]
    )
)
class BaseAttrViewSet(mixins.DestroyModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.ListModelMixin,
                      viewsets.GenericViewSet):
    """View to manage designer API"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter queryset to authenticated user.
        if assigned_only is not set its default value will be 0
        bool() will convert integer provide (1 or 0) to appropriate boolean
        """
        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', 0))
        )
        queryset = self.queryset
        # If assigned_only is True that we are going to apply another filter
        if assigned_only:
            """
            Here, perfume is a foreign key field in the model for this queryset, 
            and isnull is a field lookup that returns True if the related field 
            is null and False otherwise. Therefore, perfume__isnull=False means 
            we want to filter out the queryset where the perfume field is not null.
            """
            queryset = queryset.filter(perfume__isnull=False)

        return queryset.order_by('-name').distinct()


class DesignerViewSet(BaseAttrViewSet):
    """View to manage designer API"""
    serializer_class = serializers.DesignerSerializer
    queryset = Designer.objects.all()


class NoteViewSet(BaseAttrViewSet):
    """View to manage note API."""
    serializer_class = serializers.NoteSerializer
    queryset = Note.objects.all()
