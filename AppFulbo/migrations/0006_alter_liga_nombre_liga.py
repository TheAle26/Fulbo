# Generated by Django 5.1.6 on 2025-02-18 21:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('AppFulbo', '0005_alter_jugador_unique_together'),
    ]

    operations = [
        migrations.AlterField(
            model_name='liga',
            name='nombre_liga',
            field=models.CharField(max_length=20, unique=True),
        ),
    ]
