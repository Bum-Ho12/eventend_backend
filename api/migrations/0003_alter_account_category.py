# Generated by Django 4.1.7 on 2023-03-02 14:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_concert_concert_picture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='category',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(1, 'Independent'), (2, 'Organization')], default=1, null=True),
        ),
    ]