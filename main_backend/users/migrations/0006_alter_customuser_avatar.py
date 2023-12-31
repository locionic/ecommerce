# Generated by Django 4.1.3 on 2023-11-13 14:32

from django.db import migrations, models
import users.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_remove_customuser_small_avatar'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='avatar',
            field=models.ImageField(blank=True, null=True, upload_to=users.models.get_avatar_path),
        ),
    ]
