# Generated by Django 5.0.2 on 2024-02-24 15:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='admin_authenticated',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='user',
            name='is_subuser',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='user',
            name='parent_user_group_name',
            field=models.TextField(default=None),
        ),
        migrations.AddField(
            model_name='user',
            name='user_group',
            field=models.TextField(default=None, unique=True),
        ),
    ]
