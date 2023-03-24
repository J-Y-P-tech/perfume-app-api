"""
Serializers for recipe APIs
"""
from rest_framework import serializers

from base.models import Perfume


class PerfumeSerializer(serializers.ModelSerializer):
    """Serializer for recipes."""

    class Meta:
        model = Perfume
        fields = ['id', 'title', 'rating', 'number_of_votes', 'gender',
                  'longevity', 'sillage', 'price_value']
        read_only_fields = ['id']


class PerfumeDetailSerializer(PerfumeSerializer):
    """Serializer for recipe detail view."""

    class Meta(PerfumeSerializer.Meta):
        fields = PerfumeSerializer.Meta.fields + ['description']
