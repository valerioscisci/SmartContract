# Generated by Django 2.0.6 on 2019-07-26 17:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('smartrest', '0006_auto_20190725_1517'),
    ]

    operations = [
        migrations.AlterField(
            model_name='misura',
            name='Codice_Tariffa',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]
