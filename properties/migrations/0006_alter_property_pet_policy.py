# Generated by Django 5.1.1 on 2024-11-16 07:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0005_alter_property_property_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='property',
            name='pet_policy',
            field=models.BooleanField(default=False),
        ),
    ]
