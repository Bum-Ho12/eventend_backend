# Generated by Django 4.1.7 on 2023-03-02 19:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0016_remove_ticket_assignee_ticket_assignee_email_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='request',
            name='phone_number',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]