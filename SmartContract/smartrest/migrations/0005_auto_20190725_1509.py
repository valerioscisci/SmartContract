# Generated by Django 2.0.6 on 2019-07-25 13:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('smartrest', '0004_auto_20190724_1232'),
    ]

    operations = [
        migrations.AlterField(
            model_name='misura',
            name='Codice_Tariffa',
            field=models.CharField(default='', max_length=50),
        ),
    ]
