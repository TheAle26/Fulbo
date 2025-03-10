# Generated by Django 5.1.6 on 2025-02-20 03:11

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('AppFulbo', '0013_remove_liga_super_presidente'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='liga',
            name='super_presidente',
            field=models.ForeignKey(blank=True, help_text='El super presidente de la liga, con privilegios especiales.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ligas_super_presididas', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='liga',
            name='presidentes',
            field=models.ManyToManyField(null=True, related_name='ligas_presididas', to=settings.AUTH_USER_MODEL),
        ),
    ]
