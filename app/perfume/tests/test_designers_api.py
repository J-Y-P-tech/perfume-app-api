"""
Tests for the tags API.
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from base.models import Designer
from perfume.serializers import DesignerSerializer

DESIGNERS_URL = reverse('perfume:designer-list')


def detail_url(designer_id):
    """Create and return a designer detail url."""
    return reverse('perfume:designer-detail', args=[designer_id])


def create_user(email='user@example.com', password='testpass123'):
    """Create and return a user."""
    return get_user_model().objects.create_user(email=email, password=password)


class PublicDesignersApiTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required for retrieving tags."""
        res = self.client.get(DESIGNERS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateDesignersApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_designers(self):
        """Test retrieving a list of designers."""
        Designer.objects.create(name='Christian Dior')
        Designer.objects.create(name='Jean Claude Ellena')

        res = self.client.get(DESIGNERS_URL)

        designers = Designer.objects.all().order_by('-name')
        # many=True --> list of objects
        serializer = DesignerSerializer(designers, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_update_designer(self):
        """Test updating a designer."""
        designer = Designer.objects.create(name='Sofia Grojhman')

        payload = {'name': 'Sofia Grojsman'}
        url = detail_url(designer.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        designer.refresh_from_db()
        self.assertEqual(designer.name, payload['name'])

    def test_delete_designer(self):
        """Test deleting a designer."""
        designer = Designer.objects.create(name='Calvin Klein')

        url = detail_url(designer.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        designers = Designer.objects.all()
        self.assertFalse(designers.exists())
