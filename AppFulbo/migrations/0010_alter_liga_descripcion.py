# Generated by Django 5.1.6 on 2025-02-18 22:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('AppFulbo', '0009_alter_liga_descripcion'),
    ]

    operations = [
        migrations.AlterField(
            model_name='liga',
            name='descripcion',
            field=models.TextField(blank=True, null=True),
        ),
    ]
