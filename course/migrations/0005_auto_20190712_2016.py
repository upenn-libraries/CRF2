# Generated by Django 2.1.5 on 2019-07-13 00:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0004_auto_20190628_1126'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='canvas_id',
            field=models.CharField(max_length=10, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='additionalenrollment',
            name='course_request',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='additional_enrollments', to='course.Request'),
        ),
        migrations.AlterField(
            model_name='request',
            name='copy_from_course',
            field=models.CharField(blank=True, default=None, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='request',
            name='title_override',
            field=models.CharField(blank=True, default=None, max_length=100, null=True),
        ),
    ]