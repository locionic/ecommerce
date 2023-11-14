from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
import asyncio
import os

def get_avatar_path_without_name(instance):
    return 'avatars/{0}'.format(instance.id)

def get_avatar_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    file_path_inside_media_root = 'avatars/{0}/{1}'.format(instance.id, filename)
    return file_path_inside_media_root

class CustomUser(AbstractUser):
    email = models.EmailField(
        _("email address"),
        unique=True,
    )
    created_at = models.DateTimeField(_("joined date"), auto_now_add=True)
    is_seller = models.BooleanField(_("seller status"), default=False)
    avatar = models.ImageField(upload_to=get_avatar_path, blank=True, null=True)

    def create_thumbnail(self):
        # If there is no image associated with this.
        # do not create thumbnail
        if not self.avatar:
            return

        # Set our max thumbnail size in a tuple (max width, max height)
        THUMBNAIL_SIZE = (200, 200)
        
        if self.avatar.name.endswith(".jpg"):
            PIL_TYPE = 'jpeg'
            FILE_EXTENSION = 'jpg'
            DJANGO_TYPE = 'image/jpeg'

        elif self.avatar.name.endswith(".png"):
            PIL_TYPE = 'png'
            FILE_EXTENSION = 'png'
            DJANGO_TYPE = 'image/png'

        elif self.avatar.name.endswith('.gif'):
            DJANGO_TYPE = 'image/gif'
            PIL_TYPE = 'gif'
            FILE_EXTENSION = 'gif'

        # Open original photo which we want to thumbnail using PIL's Image
        image = Image.open(BytesIO(self.avatar.read()))

        # use our PIL Image object to create the thumbnail, which already
        image.thumbnail(THUMBNAIL_SIZE, Image.ANTIALIAS)

        # Save the thumbnail
        temp_handle = BytesIO()
        image.save(temp_handle, PIL_TYPE)
        temp_handle.seek(0)

        # Save image to a SimpleUploadedFile which can be saved into ImageField
        print(os.path.split(self.avatar.name)[-1])
        suf = SimpleUploadedFile(os.path.split(self.avatar.name)[-1],
                                 temp_handle.read(), content_type=DJANGO_TYPE)

        # Save SimpleUploadedFile into image field
        # print(os.path.splitext(suf.name)[0])
        self.avatar.save(
            '%s.%s' % (os.path.splitext(suf.name)[0], FILE_EXTENSION),
            suf, save=False)

    def save(self, *args, **kwargs):
        # asyncio.run(self.create_thumbnail())
        self.create_thumbnail()
        super(CustomUser, self).save()
