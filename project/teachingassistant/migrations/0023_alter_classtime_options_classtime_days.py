# Generated by Django 4.0.1 on 2022-03-02 01:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teachingassistant', '0022_remove_classtime_semester'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='classtime',
            options={'verbose_name': 'Class Time', 'verbose_name_plural': 'Class Times'},
        ),
        migrations.AddField(
            model_name='classtime',
            name='days',
            field=models.CharField(blank=True, max_length=10, null=True, verbose_name='Days'),
        ),
    ]
