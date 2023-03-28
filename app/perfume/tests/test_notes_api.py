"""
Tests for the notes API.
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from base.models import Note, Perfume
from perfume.serializers import NoteSerializer

from decimal import Decimal

NOTES_URL = reverse('perfume:note-list')


def detail_url(note_id):
    """Create and return a note detail url."""
    return reverse('perfume:note-detail', args=[note_id])


def create_user(email='user@example.com', password='testpass123'):
    """Create and return a user."""
    return get_user_model().objects.create_user(email=email, password=password)


class PublicNotesApiTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required for retrieving tags."""
        res = self.client.get(NOTES_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateNotesApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_notes(self):
        """Test retrieving a list of notes."""
        Note.objects.create(name='Hedione', type=1)
        Note.objects.create(name='Vetiver', type=0)

        res = self.client.get(NOTES_URL)

        notes = Note.objects.all().order_by('-name')
        # many=True --> list of objects
        serializer = NoteSerializer(notes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_update_notes(self):
        """Test updating a note."""
        note = Note.objects.create(name='Vanillin', type=0)

        payload = {'name': 'Ethyl Maltol', 'type': 0}
        url = detail_url(note.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        note.refresh_from_db()
        self.assertEqual(note.name, payload['name'])

    def test_delete_note(self):
        """Test deleting a note."""
        note = Note.objects.create(name='Galaxolide', type=0)

        url = detail_url(note.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        notes = Note.objects.all()
        self.assertFalse(notes.exists())

    def test_filter_notes_assigned_to_perfumes(self):
        """Test listing notes to those assigned to perfumes."""
        note1 = Note.objects.create(name='Note 1', type=0)
        note2 = Note.objects.create(name='Note 2', type=1)
        perfume = Perfume.objects.create(
            user=self.user,
            title='Sample perfume name',
            rating=Decimal('5.50'),
            number_of_votes=2500,
            gender=0,
            longevity=Decimal('6.1'),
            sillage=Decimal('4.2'),
            price_value=Decimal('7.0'),
            description="Perfume description.",
        )
        perfume.notes.add(note1)
        # Filter only notes that are assigned to a perfume
        # we have assigned 1 note this one should be returned
        # ‘assigned_only’: 1 will return tag once even if it appears
        # on many perfumes
        res = self.client.get(NOTES_URL, {'assigned_only': 1})

        s1 = NoteSerializer(note1)
        s2 = NoteSerializer(note2)
        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filtered_notes_unique(self):
        """Test filtered notes returns a unique list.
        We assign one note to 2 recipes and make sure that the API
        returns only one result (unique)
        """
        note1 = Note.objects.create(name='Note 1', type=0)
        Note.objects.create(name='Note 2', type=1)
        perfume1 = Perfume.objects.create(
            user=self.user,
            title='Sample perfume name',
            rating=Decimal('5.50'),
            number_of_votes=2500,
            gender=0,
            longevity=Decimal('6.1'),
            sillage=Decimal('4.2'),
            price_value=Decimal('7.0'),
            description="Perfume description.",
        )
        perfume2 = Perfume.objects.create(
            user=self.user,
            title='Sample perfume name',
            rating=Decimal('5.50'),
            number_of_votes=2500,
            gender=0,
            longevity=Decimal('6.1'),
            sillage=Decimal('4.2'),
            price_value=Decimal('7.0'),
            description="Perfume description.",
        )
        perfume1.notes.add(note1)
        perfume2.notes.add(note1)

        res = self.client.get(NOTES_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)
