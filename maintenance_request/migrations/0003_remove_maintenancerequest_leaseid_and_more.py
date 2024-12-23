# Generated by Django 5.1.1 on 2024-12-07 16:55

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maintenance_request', '0002_maintenancerequest_subject'),
        ('properties', '0008_property_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='maintenancerequest',
            name='leaseId',
        ),
        migrations.AddField(
            model_name='maintenancerequest',
            name='propertyId',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='properties.property'),
        ),
        migrations.AlterField(
            model_name='maintenancerequest',
            name='subject',
            field=models.TextField(),
        ),
    ]
