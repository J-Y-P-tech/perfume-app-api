"""
Tests for recipe APIs.
"""
from decimal import Decimal
import tempfile
import os

from PIL import Image

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from base.models import Perfume, Designer, Note

from perfume.serializers import (
    PerfumeSerializer,
    PerfumeDetailSerializer,
)

PERFUMES_URL = reverse('perfume:perfume-list')


def detail_url(perfume_id):
    """Create and return a recipe detail URL.
    http://localhost/api/perfume/1/
    """
    return reverse('perfume:perfume-detail', args=[perfume_id])


def image_upload_url(perfume_id):
    """Create and return an image upload URL.
    /api/perfumes/<id>/upload-image/
    """
    return reverse('perfume:perfume-upload-image', args=[perfume_id])


def create_perfume(user, **params):
    """Create and return a record in perfume database.
    Helper function to create perfume record for the tests
    """
    defaults = {
        'title': 'Sample perfume name',
        'rating': Decimal('5.50'),
        'number_of_votes': 2500,
        'gender': 0,
        'longevity': Decimal('6.1'),
        'sillage': Decimal('4.2'),
        'price_value': Decimal('7.0'),
        'description': "Perfume description.",
    }
    # This updates the defaults with any values,
    # provided in params (if we provide any)
    # if we do not provide any params it will use the defaults
    defaults.update(params)

    perfume = Perfume.objects.create(user=user, **defaults)
    return perfume


def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


class PublicPerfumeAPITests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API."""
        res = self.client.get(PERFUMES_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivatePerfumeApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='user@example.com',
            password='testpass123',
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_perfumes(self):
        """Test retrieving a list of recipes."""
        create_perfume(user=self.user)
        create_perfume(user=self.user)

        res = self.client.get(PERFUMES_URL)

        perfumes = Perfume.objects.all().order_by('-id')
        # many=True --> serializer will return a list of items
        serializer = PerfumeSerializer(perfumes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_perfume_list_limited_to_user(self):
        """Test list of recipes is limited to authenticated user."""
        other_user = get_user_model().objects.create_user(
            'other@example.com',
            'password123',
        )

        create_perfume(user=other_user)
        create_perfume(user=self.user)

        res = self.client.get(PERFUMES_URL)

        recipes = Perfume.objects.filter(user=self.user)
        serializer = PerfumeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_perfume_detail(self):
        """Test get recipe detail."""
        perfume = create_perfume(user=self.user)

        url = detail_url(perfume.id)
        res = self.client.get(url)

        # It is 1 recipe that's why we do not pass many=True
        serializer = PerfumeDetailSerializer(perfume)
        self.assertEqual(res.data, serializer.data)

    def test_create_perfume(self):
        """Test creating a perfume."""
        payload = {
            'title': 'Sample perfume name',
            'rating': Decimal('5.50'),
            'number_of_votes': 2500,
            'gender': 0,
            'longevity': Decimal('6.1'),
            'sillage': Decimal('4.2'),
            'price_value': Decimal('7.0'),
            'description': "Perfume description.",
        }
        res = self.client.post(PERFUMES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        perfume = Perfume.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(perfume, key))

    def test_partial_update(self):
        """Test partial update of perfume."""
        perfume = create_perfume(
            user=self.user,
            rating=Decimal('5.50'),
            number_of_votes=2500,
        )

        payload = {
            'rating': Decimal('5.10'),
            'number_of_votes': 3100,
        }

        url = detail_url(perfume.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        perfume.refresh_from_db()
        self.assertEqual(perfume.rating, payload['rating'])
        self.assertEqual(perfume.number_of_votes, payload['number_of_votes'])
        self.assertEqual(perfume.user, self.user)

    def test_full_update(self):
        """Test full update of perfume."""
        perfume = create_perfume(
            user=self.user,
            rating=Decimal('5.50'),
            number_of_votes=2500,
        )

        payload = {
            'title': 'Fully updated perfume name',
            'rating': Decimal('5.00'),
            'number_of_votes': 4300,
            'gender': 0,
            'longevity': Decimal('6.0'),
            'sillage': Decimal('4.0'),
            'price_value': Decimal('6.0'),
            'description': "Perfume updated description.",
        }
        url = detail_url(perfume.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        perfume.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(perfume, k), v)
        self.assertEqual(perfume.user, self.user)

    def test_update_user_returns_error(self):
        """Test changing the perfume user results in an error."""
        new_user = create_user(email='user2@example.com', password='test123')
        perfume = create_perfume(user=self.user)

        payload = {'user': new_user.id}
        url = detail_url(perfume.id)
        self.client.patch(url, payload)

        perfume.refresh_from_db()
        self.assertEqual(perfume.user, self.user)

    def test_delete_perfume(self):
        """Test deleting a recipe successful."""
        perfume = create_perfume(user=self.user)

        url = detail_url(perfume.id)
        res = self.client.delete(url)

        # HTTP_204_NO_CONTENT is the default response for Delete
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Perfume.objects.filter(id=perfume.id).exists())

    def test_delete_other_users_perfume_error(self):
        """Test trying to delete another users perfume gives error."""
        new_user = create_user(email='user2@example.com', password='test123')
        perfume = create_perfume(user=new_user)

        url = detail_url(perfume.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Perfume.objects.filter(id=perfume.id).exists())

    def test_perfume_with_new_designers(self):
        """Test creating a perfume with new designers."""
        payload = {
            'title': 'Sample perfume name',
            'rating': Decimal('5.50'),
            'number_of_votes': 2500,
            'gender': 0,
            'longevity': Decimal('6.1'),
            'sillage': Decimal('4.2'),
            'price_value': Decimal('7.0'),
            'description': "Perfume description.",
            'designers': [{'name': 'Christian Dion'}, {'name': 'Bulgari'}],
        }
        res = self.client.post(PERFUMES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        perfumes = Perfume.objects.filter(user=self.user)
        self.assertEqual(perfumes.count(), 1)
        perfume = perfumes[0]
        self.assertEqual(perfume.designers.count(), 2)
        for designer in payload['designers']:
            exists = perfume.designers.filter(
                name=designer['name'],
            ).exists()
            self.assertTrue(exists)

    def test_create_perfume_with_existing_designers(self):
        """Test creating a recipe with existing designer."""
        designer_1 = Designer.objects.create(name='Designer 1')
        payload = {
            'title': 'Sample perfume name',
            'rating': Decimal('5.50'),
            'number_of_votes': 2500,
            'gender': 0,
            'longevity': Decimal('6.1'),
            'sillage': Decimal('4.2'),
            'price_value': Decimal('7.0'),
            'description': "Perfume description.",
            'designers': [{'name': 'Christian Dion'}, {'name': 'Designer 1'}],
        }
        res = self.client.post(PERFUMES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        perfumes = Perfume.objects.filter(user=self.user)
        self.assertEqual(perfumes.count(), 1)
        perfume = perfumes[0]
        self.assertEqual(perfume.designers.count(), 2)
        self.assertIn(designer_1, perfume.designers.all())
        for designer in payload['designers']:
            exists = perfume.designers.filter(
                name=designer['name'],
            ).exists()
            self.assertTrue(exists)

    def test_create_designer_on_update(self):
        """Test create designer when updating a perfume."""
        perfume = create_perfume(user=self.user)

        payload = {'designers': [{'name': 'Luis Vuton'}]}
        url = detail_url(perfume.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_designer = Designer.objects.get(name='Luis Vuton')
        self.assertIn(new_designer, perfume.designers.all())

    def test_update_perfume_assign_designer(self):
        """Test assigning an existing designer when updating a perfume."""
        designer_one = Designer.objects.create(name='Designer One')
        perfume = create_perfume(user=self.user)
        perfume.designers.add(designer_one)

        designer_two = Designer.objects.create(name='Designer Two')
        payload = {'designers': [{'name': 'Designer Two'}]}
        url = detail_url(perfume.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(designer_two, perfume.designers.all())
        self.assertNotIn(designer_one, perfume.designers.all())

    def test_clear_perfume_designers(self):
        """Test clearing a perfume designers."""
        designer = Designer.objects.create(name='Karl Lagerfelt')
        perfume = create_perfume(user=self.user)
        perfume.designers.add(designer)

        payload = {'designers': []}
        url = detail_url(perfume.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(perfume.designers.count(), 0)

    def test_perfume_with_new_notes(self):
        """Test creating a perfume with new notes."""
        payload = {
            'title': 'Sample perfume name',
            'rating': Decimal('5.50'),
            'number_of_votes': 2500,
            'gender': 0,
            'longevity': Decimal('6.1'),
            'sillage': Decimal('4.2'),
            'price_value': Decimal('7.0'),
            'description': "Perfume description.",
            'notes': [{'name': 'Patchouli', 'type': 0},
                      {'name': 'Rose Oil', 'type': 1}],
        }
        res = self.client.post(PERFUMES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        perfumes = Perfume.objects.filter(user=self.user)
        self.assertEqual(perfumes.count(), 1)
        perfume = perfumes[0]
        self.assertEqual(perfume.notes.count(), 2)
        for note in payload['notes']:
            exists = perfume.notes.filter(
                name=note['name'],
                type=note['type'],
            ).exists()
            self.assertTrue(exists)

    def test_create_perfume_with_existing_notes(self):
        """Test creating a perfume with existing note."""
        note_1 = Note.objects.create(name='Olibanum', type=1)
        payload = {
            'title': 'Sample perfume name',
            'rating': Decimal('5.50'),
            'number_of_votes': 2500,
            'gender': 0,
            'longevity': Decimal('6.1'),
            'sillage': Decimal('4.2'),
            'price_value': Decimal('7.0'),
            'description': "Perfume description.",
            'notes': [{'name': 'Romandolide', 'type': 0},
                      {'name': 'Olibanum', 'type': 1}],
        }
        res = self.client.post(PERFUMES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        perfumes = Perfume.objects.filter(user=self.user)
        self.assertEqual(perfumes.count(), 1)
        perfume = perfumes[0]
        self.assertEqual(perfume.notes.count(), 2)
        self.assertIn(note_1, perfume.notes.all())
        for note in payload['notes']:
            exists = perfume.notes.filter(
                name=note['name'],
                type=note['type'],
            ).exists()
            self.assertTrue(exists)

    def test_create_note_on_update(self):
        """Test create note when updating a perfume."""
        perfume = create_perfume(user=self.user)

        payload = {'notes': [{'name': 'Patchouli', 'type': 0}]}
        url = detail_url(perfume.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_note = Note.objects.get(name='Patchouli', type=0)
        self.assertIn(new_note, perfume.notes.all())

    def test_update_perfume_assign_note(self):
        """Test assigning an existing note when updating a perfume."""
        note_one = Note.objects.create(name='Patchouli', type=0)
        perfume = create_perfume(user=self.user)
        perfume.notes.add(note_one)

        note_two = Note.objects.create(name='Vetiver', type=0)
        payload = {'notes': [{'name': 'Vetiver', 'type': 0}]}
        url = detail_url(perfume.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(note_two, perfume.notes.all())
        self.assertNotIn(note_one, perfume.notes.all())

    def test_clear_perfume_notes(self):
        """Test clearing a perfume notes."""
        note = Note.objects.create(name='Ethyl Vanillin', type=0)
        perfume = create_perfume(user=self.user)
        perfume.notes.add(note)

        payload = {'notes': []}
        url = detail_url(perfume.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(perfume.notes.count(), 0)

    def test_filter_by_designers(self):
        """Test filtering perfumes by designers."""
        p1 = create_perfume(user=self.user, title='Perufme 1')
        p2 = create_perfume(user=self.user, title='Perfume 2')
        designer1 = Designer.objects.create(name='Designer 1')
        designer2 = Designer.objects.create(name='Designer 2')
        p1.designers.add(designer1)
        p2.designers.add(designer2)
        p3 = create_perfume(user=self.user, title='Perfume 3')

        params = {'designers': f'{designer1.id},{designer2.id}'}
        res = self.client.get(PERFUMES_URL, params)

        s1 = PerfumeSerializer(p1)
        s2 = PerfumeSerializer(p2)
        s3 = PerfumeSerializer(p3)
        self.assertIn(s1.data, res.data)
        self.assertIn(s2.data, res.data)
        self.assertNotIn(s3.data, res.data)

    def test_filter_by_notes(self):
        """Test filtering perfumes by notes."""
        p1 = create_perfume(user=self.user, title='Perufme 1')
        p2 = create_perfume(user=self.user, title='Perfume 2')
        note1 = Note.objects.create(name='Note 1', type=0)
        note2 = Note.objects.create(name='Note 2', type=1)
        p1.notes.add(note1)
        p2.notes.add(note2)
        p3 = create_perfume(user=self.user, title='Perfume 3')

        params = {'notes': f'{note1.id},{note2.id}'}
        res = self.client.get(PERFUMES_URL, params)

        s1 = PerfumeSerializer(p1)
        s2 = PerfumeSerializer(p2)
        s3 = PerfumeSerializer(p3)
        self.assertIn(s1.data, res.data)
        self.assertIn(s2.data, res.data)
        self.assertNotIn(s3.data, res.data)


class ImageUploadTests(TestCase):
    """Tests for the image upload API."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@example.com',
            'password123',
        )
        self.client.force_authenticate(self.user)
        self.perfume = create_perfume(user=self.user)

    def tearDown(self):
        self.perfume.image.delete()

    def test_upload_image(self):
        """Test uploading an image to a perfume."""
        url = image_upload_url(self.perfume.id)
        """
        This is a helper module that's provided by Python, which allows you to create 
        temporary files when you're working with Python code.        
        So while we're in this block that says with tempfile.NamedTemporaryFile
        as image file, all the code that's in here, it's going to have a temporary file 
        created that we can use. And then as soon as this ends, it's going to clean up, 
        file out for us all nicely. So we're using this name temporary file to create a 
        temporary image file that we can use to test uploading to our endpoint.
        """
        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            # Creates basic test image, black 10 by 10 pixels
            img = Image.new('RGB', (10, 10))
            # Save file to file system
            img.save(image_file, format='JPEG')
            # seeks back to the beginning of the file because
            # img.save() moves pointer to the end of the file
            image_file.seek(0)
            payload = {'image': image_file}
            # format='multipart' contains text and binary data
            res = self.client.post(url, payload, format='multipart')

        self.perfume.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.perfume.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image."""
        url = image_upload_url(self.perfume.id)
        payload = {'image': 'notanimage'}
        res = self.client.post(url, payload, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
