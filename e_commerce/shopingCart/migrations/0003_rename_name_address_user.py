# Generated by Django 5.1.2 on 2024-10-30 06:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shopingCart', '0002_address'),
    ]

    operations = [
        migrations.RenameField(
            model_name='address',
            old_name='name',
            new_name='user',
        ),
    ]
