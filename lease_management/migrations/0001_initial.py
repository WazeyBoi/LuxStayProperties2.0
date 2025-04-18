# Generated by Django 5.1.1 on 2024-11-02 11:04

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Lease',
            fields=[
                ('leaseId', models.AutoField(primary_key=True, serialize=False)),
                ('propertyId', models.CharField(max_length=100)),
                ('tenantId', models.CharField(max_length=100)),
                ('startDate', models.DateField()),
                ('endDate', models.DateField()),
                ('totalAmount', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
        ),
    ]
