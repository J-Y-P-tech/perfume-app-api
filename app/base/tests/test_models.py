"""
Tests for models.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from base import models
from decimal import Decimal

"""
get_user_model helper function is provided by Django in order to get the default user model
for the project. Now you can reference the model directly from the models that we're going to define.
After we write this test, however, it's best practice to use get_user_model so that if you ever do
decide to change the user model, then it will be automatically updated everywhere in your code because
as long as you use the user model function to retrieve your custom user model, you will always be able
to get the default model as configured for that product.
So when you're using the Django user model, it's best to use this get_user_model function in order
to get a reference to your custom user model.
"""


def create_user(email='user@example.com', password='testpass123'):
    """Create a return a new user."""
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):
    """Test models."""

    def test_create_user_with_email_successful(self):
        """Test creating a user with an email is successful."""
        email = 'test@example.com'
        password = 'testpass123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test email is normalized for new users."""
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.com', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'sample123')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test that creating a user without an email raises a ValueError."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'test123')

    def test_create_superuser(self):
        """Test creating a superuser."""
        user = get_user_model().objects.create_superuser(
            'test@example.com',
            'test123',
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_perfume(self):
        """Test creating a perfume record is successful."""

        user = get_user_model().objects.create_user(
            'test@example.com',
            'testpass123',
        )

        # note1, created = models.Note.objects.get_or_create(
        #     note_name="Bergamot",
        #     note_type=2,
        # )
        #
        # note2, created = models.Note.objects.get_or_create(
        #     note_name="Patchouli",
        #     note_type=0,
        # )
        #
        # designer1, created = models.Designer.objects.get_or_create(
        #     designer_name="Jean claude Ellena",
        # )

        perfume = models.Perfume.objects.create(
            user=user,
            title='Sample perfume name',
            rating=Decimal('5.50'),
            number_of_votes=2500,
            gender=0,
            longevity=Decimal('6.1'),
            sillage=Decimal('4.2'),
            price_value=Decimal('7.0'),
            description="Perfume description.",
        )

        # perfume.notes.set([note1, note2])
        # perfume.designers.set([designer1])

        self.assertEqual(str(perfume), perfume.title)

    def test_create_designer(self):
        designer = models.Designer.objects.create(name='Christian Dior')
        self.assertEqual(str(designer), designer.name)

    def test_create_note(self):
        """Test creating a note is successful."""
        note = models.Note.objects.create(
            type=0,
            name='Patchouli'
        )

        self.assertEqual(str(note), note.name)
