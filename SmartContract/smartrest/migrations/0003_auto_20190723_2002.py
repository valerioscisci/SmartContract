# Generated by Django 2.0.6 on 2019-07-23 18:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('smartrest', '0002_contratto_lavoro_misure'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Misure',
            new_name='Misura',
        ),
    ]