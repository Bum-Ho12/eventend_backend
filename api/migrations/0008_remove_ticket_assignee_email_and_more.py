# Generated by Django 4.1.7 on 2023-03-17 11:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_remove_request_client_id_remove_request_client_name_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ticket',
            name='assignee_email',
        ),
        migrations.RemoveField(
            model_name='ticket',
            name='assignee_id',
        ),
        migrations.RemoveField(
            model_name='ticket',
            name='assignee_name',
        ),
        migrations.RemoveField(
            model_name='ticket',
            name='assignee_picture',
        ),
        migrations.RemoveField(
            model_name='ticket',
            name='concert_id',
        ),
        migrations.RemoveField(
            model_name='ticket',
            name='concert_picture',
        ),
        migrations.RemoveField(
            model_name='ticket',
            name='description',
        ),
        migrations.RemoveField(
            model_name='ticket',
            name='phone_number',
        ),
        migrations.RemoveField(
            model_name='ticket',
            name='title',
        ),
        migrations.AddField(
            model_name='ticket',
            name='assignee',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='assignee', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='ticket',
            name='concert',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='api.concert'),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='ticket_number',
            field=models.TextField(blank=True, null=True),
        ),
    ]
