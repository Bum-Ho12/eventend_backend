# Generated by Django 4.1.7 on 2023-03-02 14:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_alter_account_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='category',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(1, 'Independent'), (2, 'Organization')], null=True),
        ),
    ]