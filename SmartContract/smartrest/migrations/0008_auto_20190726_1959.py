# Generated by Django 2.0.6 on 2019-07-26 17:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('smartrest', '0007_auto_20190726_1944'),
    ]

    operations = [
        migrations.AlterField(
            model_name='misura',
            name='Altezza_Peso',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='misura',
            name='Larghezza',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='misura',
            name='Lunghezza',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='misura',
            name='Negativi',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='misura',
            name='Parti_Uguali',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
