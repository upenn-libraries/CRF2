# Generated by Django 2.1.5 on 2019-04-05 14:31

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0004_auto_20190403_2030'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='instructors',
            field=models.ManyToManyField(blank=True, related_name='courses', to=settings.AUTH_USER_MODEL),
        ),
    ]
