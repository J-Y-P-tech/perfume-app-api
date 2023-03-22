"""
Database models.
"""
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


class UserManager(BaseUserManager):
    """Manager for users."""

    def create_user(self, email, password=None, **extra_fields):
        """Create, save and return a new user.

        password=None --> If we want to create a User without password
        for test purposes
        **extra_fields --> we can provide keyword arguments,
        any number of keyword arguments that will be passed into our model
        This is useful when you define additional fields, for example, a name,
        you can pass it as an extra field and that will be automatically created
        when the user model is created. And it just gives you a bit of flexibility
        when it comes to creating different fields in a user.
        self.model --> is the same as creating new User() object because that is
        the manager the user is going to be assigned to.
        email is main filed and the others are passed as extra.
        """
        if not email:
            raise ValueError("User must have an email address.")

        user = self.model(email=self.normalize_email(email), **extra_fields)
        # It will take the password provided in the create user method
        # and encrypt through a hashing mechanism.
        user.set_password(password)
        # using=self._db --> allow us to add multiple databases,
        # although it is rarely used
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """ Create and return a new superuser. """
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system.

    AbstractBaseUser contains the functionality for the authentication system, but not any fields.
    PermissionsMixin contains the functionality for the permissions feature of Django, and it also contains any fields
    that are needed for the permissions feature.
    """
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
