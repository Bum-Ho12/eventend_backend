# Generated by Django 4.1.7 on 2023-03-18 06:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_ticket_receipt'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='isCustomer',
            field=models.BooleanField(blank=True, default=True, null=True),
        ),
    ]
