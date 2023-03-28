"""
Serializers for recipe APIs
"""
from rest_framework import serializers

from base.models import Perfume, Designer, Note


class DesignerSerializer(serializers.ModelSerializer):
    """Serializer for designers. """

    class Meta:
        model = Designer
        fields = ['id', 'name']
        read_only_field = ['id']


class NoteSerializer(serializers.ModelSerializer):
    """Serializer for notes."""

    class Meta:
        model = Note
        fields = ['id', 'name', 'type']
        read_only_fields = ['id']


class PerfumeImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading images to perfumes."""

    class Meta:
        model = Perfume
        fields = ['id', 'image']
        read_only_fields = ['id']
        extra_kwargs = {'image': {'required': 'True'}}


class PerfumeSerializer(serializers.ModelSerializer):
    """Serializer for perfumes."""
    designers = DesignerSerializer(many=True, required=False)
    notes = NoteSerializer(many=True, required=False)

    class Meta:
        model = Perfume
        fields = ['id', 'title', 'rating', 'number_of_votes', 'gender',
                  'longevity', 'sillage', 'price_value', 'designers', 'notes']
        read_only_fields = ['id']


class PerfumeDetailSerializer(PerfumeSerializer):
    """Serializer for perfume detail view."""

    class Meta(PerfumeSerializer.Meta):
        fields = PerfumeSerializer.Meta.fields + ['description', 'image']

    @staticmethod
    def _get_or_create_designers(designers, perfume):
        """Handle getting or creating designers as needed."""
        for designer in designers:
            designer_obj, created = Designer.objects.get_or_create(
                **designer,
            )
            perfume.designers.add(designer_obj)

    @staticmethod
    def _get_or_create_notes(notes, perfume):
        """Handle getting or creating notes as needed."""
        for note in notes:
            note_obj, created = Note.objects.get_or_create(
                **note,
            )
            perfume.notes.add(note_obj)

    def create(self, validated_data):
        """Create a perfume.
        By default, nested serializers are read-only
        that's why we will override create()
        """
        # removes designers from validated data and assign's it to variable designers
        designers = validated_data.pop('designers', [])
        notes = validated_data.pop('notes', [])
        perfume = Perfume.objects.create(**validated_data)
        self._get_or_create_designers(designers, perfume)
        self._get_or_create_notes(notes, perfume)
        return perfume

    # instance is the existing data
    # validated_data is the new one that will be added
    def update(self, instance, validated_data):
        """Update perfume."""

        designers = validated_data.pop('designers', None)
        if designers is not None:
            instance.designers.clear()
            self._get_or_create_designers(designers, instance)

        notes = validated_data.pop('notes', None)
        if notes is not None:
            instance.notes.clear()
            self._get_or_create_notes(notes, instance)

        # everything else will be updated
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
