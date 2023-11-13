from djoser.serializers import UserSerializer as djoser_UserSerializer
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "email", "avatar"]


# initialize the shown fields of UserSerializer of djoser
djoser_UserSerializer.Meta.fields = ["first_name", "last_name", "username", "email"]
djoser_UserSerializer.Meta.read_only_fields += ('created_at',)


class CurrentUserSerializer(djoser_UserSerializer):
    class Meta(djoser_UserSerializer.Meta):
        fields = ["first_name", "last_name", "username", "email", "created_at", "is_seller", "is_staff", "avatar"]
        read_only_fields = djoser_UserSerializer.Meta.read_only_fields + ('created_at',)

class Base64ImageField(serializers.ImageField):
    """
    A Django REST framework field for handling image-uploads through raw post data.
    It uses base64 for encoding and decoding the contents of the file.

    Heavily based on
    https://github.com/tomchristie/django-rest-framework/pull/1268

    Updated for Django REST framework 3.
    """

    def to_internal_value(self, data):
        from django.core.files.base import ContentFile
        import base64
        import six
        import uuid

        # Check if this is a base64 string
        if isinstance(data, six.string_types):
            # Check if the base64 string is in the "data:" format
            if 'data:' in data and ';base64,' in data:
                # Break out the header from the base64 content
                header, data = data.split(';base64,')

            # Try to decode the file. Return validation error if it fails.
            try:
                decoded_file = base64.b64decode(data)
            except TypeError:
                self.fail('invalid_image')

            # Generate file name:
            file_name = str(uuid.uuid4())[:12] # 12 characters are more than enough.
            # Get the file name extension:
            file_extension = self.get_file_extension(file_name, decoded_file)

            complete_file_name = "%s.%s" % (file_name, file_extension, )

            data = ContentFile(decoded_file, name=complete_file_name)

        return super(Base64ImageField, self).to_internal_value(data)

    def get_file_extension(self, file_name, decoded_file):
        import imghdr

        extension = imghdr.what(file_name, decoded_file)
        extension = "jpg" if extension == "jpeg" else extension

        return extension

class UserPostPutPatchSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(
        max_length=None, use_url=True, required=False,
        allow_null=True
    )
    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "email", "avatar"]
        extra_kwargs = {
            'avatar': {'required': False}
        }