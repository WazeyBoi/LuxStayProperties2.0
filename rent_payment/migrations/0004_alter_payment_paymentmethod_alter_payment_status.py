# Generated by Django 5.1.1 on 2024-11-16 14:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rent_payment', '0003_alter_payment_leaseid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='paymentMethod',
            field=models.CharField(choices=[('cash', 'Cash'), ('credit_card', 'Credit Card'), ('debit_card', 'Debit Card')], default='cash', max_length=20),
        ),
        migrations.AlterField(
            model_name='payment',
            name='status',
            field=models.CharField(choices=[('paid', 'Paid'), ('unpaid', 'Unpaid')], default='unpaid', max_length=10),
        ),
    ]
