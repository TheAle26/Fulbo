# Generated by Django 5.1.6 on 2025-02-13 20:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('AppFulbo', '0002_delete_perfilusuario'),
    ]

    operations = [
        migrations.RenameField(
            model_name='jugador',
            old_name='apellido',
            new_name='apodo',
        ),
        migrations.RenameField(
            model_name='jugador',
            old_name='posicion_favorita',
            new_name='posicion',
        ),
        migrations.RemoveField(
            model_name='jugador',
            name='nombre',
        ),
    ]
