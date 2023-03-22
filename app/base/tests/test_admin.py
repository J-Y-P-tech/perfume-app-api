"""
Tests for the Django admin modifications.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client

""""
The Client class is a test client that provides a way to simulate HTTP requests to your Django application. 
You can use it to test your views and other components of your application that handle HTTP requests and responses.
For example, you can use the Client class to test the response of a view function by making a GET or POST request 
to the URL that corresponds to that view. You can then check the response status code, headers, and content 
to ensure that the view is behaving as expected.
"""


class AdminSiteTests(TestCase):
    """Tests for Django admin."""

    def setUp(self):
        """Create user and client.
        This code will be run before every single Test that we perform
        The name of this method should be this not set-up
        """
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email='admin@example.com',
            password='testpass123',
        )
        self.client.force_login(self.admin_user)
        # We will log in as admin User
        self.user = get_user_model().objects.create_user(
            email='user@example.com',
            password='testpass123',
            name='Test User'
        )

    def test_users_lists(self):
        """Test that users are listed on page."""
        url = reverse('admin:base_user_changelist')
        #  http://127.0.0.1:8000/admin/base/user/1/change/
        # This will get the page where Users are listed
        res = self.client.get(url)

        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_edit_user_page(self):
        """Test the edit user page works."""
        url = reverse('admin:base_user_change', args=[self.user.id])
        # http://127.0.0.1:8000/admin/base/user/1/change/
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        """Test the create user page works."""
        url = reverse('admin:base_user_add')
        # http://127.0.0.1:8000/admin/base/user/add/
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
