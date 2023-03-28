"""
Tests for the designers API.
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from base.models import Designer, Perfume
from perfume.serializers import DesignerSerializer

from decimal import Decimal

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

    def test_filter_designers_assigned_to_perfumes(self):
        """Test listing designers to those assigned to perfumes."""
        designer1 = Designer.objects.create(name='Designer1')
        designer2 = Designer.objects.create(name='Designer2')
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
        perfume.designers.add(designer1)

        res = self.client.get(DESIGNERS_URL, {'assigned_only': 1})

        s1 = DesignerSerializer(designer1)
        s2 = DesignerSerializer(designer2)
        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filtered_designers_unique(self):
        """Test filtered designers returns a unique list."""
        designer = Designer.objects.create(name='Designer1')
        Designer.objects.create(name='Designer2')
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
        perfume1.designers.add(designer)
        perfume2.designers.add(designer)

        """
        When the request is made with the query parameter {'assigned_only': 1}, it should only 
        return a single DESIGNER (ing) since it is the only one that is assigned to a recipe.
        """
        res = self.client.get(DESIGNERS_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)
