# Generated by Django 4.0.1 on 2022-03-01 20:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teachingassistant', '0020_remove_availability_friday_end_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='classtime',
            name='semester',
            field=models.CharField(blank=True, max_length=10, null=True, verbose_name='Semester'),
        ),
    ]
