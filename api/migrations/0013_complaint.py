# Generated by Django 4.1.7 on 2023-03-22 15:05

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0012_concert_advertise_service_advertise'),
    ]

    operations = [
        migrations.CreateModel(
            name='Complaint',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(blank=True, max_length=600)),
                ('Service', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='api.service')),
                ('concert', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='api.concert')),
                ('owner', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='complainant', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Complaints',
            },
        ),
    ]
