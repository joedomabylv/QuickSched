# Generated by Django 4.0.1 on 2022-02-16 03:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teachingassistant', '0004_alter_ta_contracted'),
    ]

    operations = [
        migrations.AlterField(
            model_name='availability',
            name='friday_end',
            field=models.TimeField(blank=True),
        ),
        migrations.AlterField(
            model_name='availability',
            name='friday_start',
            field=models.TimeField(blank=True),
        ),
        migrations.AlterField(
            model_name='availability',
            name='monday_end',
            field=models.TimeField(blank=True),
        ),
        migrations.AlterField(
            model_name='availability',
            name='monday_start',
            field=models.TimeField(blank=True),
        ),
        migrations.AlterField(
            model_name='availability',
            name='saturday_end',
            field=models.TimeField(blank=True),
        ),
        migrations.AlterField(
            model_name='availability',
            name='saturday_start',
            field=models.TimeField(blank=True),
        ),
        migrations.AlterField(
            model_name='availability',
            name='sunday_end',
            field=models.TimeField(blank=True),
        ),
        migrations.AlterField(
            model_name='availability',
            name='sunday_start',
            field=models.TimeField(blank=True),
        ),
        migrations.AlterField(
            model_name='availability',
            name='thursday_end',
            field=models.TimeField(blank=True),
        ),
        migrations.AlterField(
            model_name='availability',
            name='thursday_start',
            field=models.TimeField(blank=True),
        ),
        migrations.AlterField(
            model_name='availability',
            name='tuesday_end',
            field=models.TimeField(blank=True),
        ),
        migrations.AlterField(
            model_name='availability',
            name='tuesday_start',
            field=models.TimeField(blank=True),
        ),
        migrations.AlterField(
            model_name='availability',
            name='wednesday_end',
            field=models.TimeField(blank=True),
        ),
        migrations.AlterField(
            model_name='availability',
            name='wednesday_start',
            field=models.TimeField(blank=True),
        ),
    ]