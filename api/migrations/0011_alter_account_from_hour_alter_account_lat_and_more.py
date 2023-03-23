# Generated by Django 4.1.7 on 2023-03-20 04:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_account_iscustomer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='from_hour',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='account',
            name='lat',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True),
        ),
        migrations.AlterField(
            model_name='account',
            name='long',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True),
        ),
        migrations.AlterField(
            model_name='account',
            name='to_hour',
            field=models.TimeField(blank=True, null=True),
        ),
    ]