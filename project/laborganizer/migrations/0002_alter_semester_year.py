# Generated by Django 4.0.1 on 2022-02-09 19:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('laborganizer', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='semester',
            name='year',
            field=models.CharField(choices=[(2022, 2022), (2023, 2023), (2024, 2024), (2025, 2025), (2026, 2026), (2027, 2027), (2028, 2028), (2029, 2029), (2030, 2030), (2031, 2031), (2032, 2032)], max_length=5, verbose_name='Calendar year'),
        ),
    ]
