# Generated by Django 2.0.6 on 2019-08-04 16:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('smartrest', '0008_auto_20190726_1959'),
    ]

    operations = [
        migrations.AddField(
            model_name='lavoro',
            name='Debito',
            field=models.FloatField(default=0.0),
        ),
    ]
