# Generated by Django 4.1.7 on 2023-03-02 16:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0012_alter_service_organizer_alter_service_organizer_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='service',
            name='web_link',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]