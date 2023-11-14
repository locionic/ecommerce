from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver
from django.shortcuts import get_object_or_404
from users.models import CustomUser, get_avatar_path_without_name
import os
from pathlib import Path
from django.conf import settings

@receiver(post_save, sender=CustomUser)
def user_save(sender, instance, **kwargs):
    """
    delete old avatar images after save function
    """
    user = get_object_or_404(CustomUser, pk=instance.pk)
    if user.avatar:
        file_except = user.avatar.name.split('/')[-1]
        for clean_up in Path(os.path.join(settings.MEDIA_ROOT, get_avatar_path_without_name(user))).iterdir():
            if clean_up.name != file_except:
                clean_up.unlink()
