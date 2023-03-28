"""
Tests for the notes API.
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from base.models import Note
from perfume.serializers import NoteSerializer

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
