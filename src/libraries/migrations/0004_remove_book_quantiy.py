# Generated by Django 5.1.1 on 2024-09-14 15:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('libraries', '0003_borrow_is_returnd'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='book',
            name='quantiy',
        ),
    ]
