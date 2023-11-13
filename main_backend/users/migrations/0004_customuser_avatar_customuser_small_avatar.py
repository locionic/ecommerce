# Generated by Django 4.1.3 on 2023-11-13 11:29

from django.db import migrations, models
import users.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_customuser_is_seller_alter_customuser_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='avatar',
            field=models.ImageField(blank=True, upload_to=users.models.get_avatar_path),
        ),
        migrations.AddField(
            model_name='customuser',
            name='small_avatar',
            field=models.ImageField(blank=True, upload_to=users.models.get_avatar_path),
        ),
    ]
