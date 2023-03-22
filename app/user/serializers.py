"""
Serializers for the user API View.
"""
from django.contrib.auth import (
    get_user_model,
    authenticate,
)
from django.utils.translation import gettext as _
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object.
    Serializer is simply just a way to convert objects to and from python objects.
    It takes adjacent input that might be posted from the API and validates
    the input to make sure that it is secure and correct as part of validation rules.
    Then it converts it to either a python object that we can use or a model in
    our actual database. So there are different base classes that you can use for the serialization.
    Model serializers allow us to  automatically validate and save things to a specific model
    that we define in our serialization.
    """

    class Meta:
        """
        Here we tell Django what should be passed to Serializer
        """
        model = get_user_model()
        # The only fields that we allow user to change
        # we don't include is_active or is_staff
        fields = ('email', 'password', 'name')
        # 'password': {'write_only': --> user will be able to set password,
        # but it will not be returned over API response
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    def create(self, validated_data):
        """Create and return a user with encrypted password.
        We're overwriting the create method so that we can call get_user_model
        object to create and then pass in the already validated
        data from our sterilizer.
        If there is a validation error this method will not be called.
        """
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update and return user.
        We override the serializer update method
        """
        # None is the default value of the password
        # retrieve the password from the validated data
        # and them remove it from the dictionary
        password = validated_data.pop('password', None)
        # instance is the module instance that will be updated
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user auth token."""
    email = serializers.EmailField()
    # style={'input_type': 'password'}, --> will secure the password while using
    # browsable API
    # trim_whitespace=False, --> user may put space at the end of the password deliberately
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
    )

    def validate(self, attrs):
        """Validate and authenticate the user."""
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password,
        )
        if not user:
            msg = _('Unable to authenticate with provided credentials.')
            # By raising this way the Error the View will get it and
            # return 404 error.
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs
