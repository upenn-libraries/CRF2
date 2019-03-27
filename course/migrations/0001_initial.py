# Generated by Django 2.1.5 on 2019-03-25 18:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AutoAdd',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('ta', 'TA'), ('instructor', 'Instructor'), ('designer', 'Designer'), ('librarian', 'Librarian')], max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='CanvasSite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField()),
            ],
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('course_term', models.CharField(choices=[('A', 'Spring'), ('B', 'Summer'), ('C', 'Fall')], max_length=1)),
                ('course_activity', models.CharField(choices=[('LEC', 'Lecture'), ('SEM', 'Seminar'), ('LAB', 'Laboratory')], max_length=3)),
                ('course_SRStitle', models.CharField(max_length=250, primary_key=True, serialize=False, unique=True)),
                ('course_name', models.CharField(max_length=250)),
                ('requested', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ('created',),
            },
        ),
        migrations.CreateModel(
            name='Notice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('notice_heading', models.CharField(max_length=100)),
                ('notice_text', models.TextField(max_length=1000)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notices', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'get_latest_by': 'updated_date',
            },
        ),
        migrations.CreateModel(
            name='School',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('abbreviation', models.CharField(max_length=10, unique=True)),
                ('visible', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('abbreviation', models.CharField(max_length=10, unique=True)),
                ('visible', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='UpdateLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Request',
            fields=[
                ('course_requested', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='course.Course')),
                ('copy_from_course', models.CharField(max_length=100, null=True)),
                ('title_override', models.CharField(blank=True, default=None, max_length=100)),
                ('additional_instructions', models.TextField(blank=True, default=None)),
                ('reserves', models.BooleanField(default=False)),
                ('status', models.CharField(choices=[('COMPLETED', 'Completed'), ('IN_PROCESS', 'In Process'), ('CANCELED', 'Canceled'), ('APPROVED', 'Approved'), ('SUBMITTED', 'Submitted'), ('LOCKED', 'Locked')], default='SUBMITTED', max_length=20)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('masquerade', models.CharField(max_length=20, null=True)),
                ('canvas_instance', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='canvas', to='course.CanvasSite')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='requests', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('created',),
            },
        ),
        migrations.AddField(
            model_name='course',
            name='course_schools',
            field=models.ManyToManyField(related_name='courses', to='course.School'),
        ),
        migrations.AddField(
            model_name='course',
            name='course_subjects',
            field=models.ManyToManyField(related_name='courses', to='course.Subject'),
        ),
        migrations.AddField(
            model_name='course',
            name='instructors',
            field=models.ManyToManyField(related_name='courses', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='course',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='autoadd',
            name='school',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='course.School'),
        ),
        migrations.AddField(
            model_name='autoadd',
            name='subject',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='course.Subject'),
        ),
        migrations.AddField(
            model_name='autoadd',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
