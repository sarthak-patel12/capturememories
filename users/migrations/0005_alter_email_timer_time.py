# Generated by Django 5.0.2 on 2024-03-08 05:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_email_timer_verification_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='email_timer',
            name='time',
            field=models.IntegerField(),
        ),
    ]
