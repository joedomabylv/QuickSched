# Generated by Django 4.0.1 on 2022-04-25 03:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teachingassistant', '0027_alter_ta_student_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='classtime',
            name='semester_name',
            field=models.TextField(blank=True, verbose_name='Semester'),
        ),
    ]
