# Generated by Django 2.0.6 on 2019-08-08 19:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('smartrest', '0010_soglia'),
    ]

    operations = [
        migrations.AddField(
            model_name='lavoro',
            name='Percentuale',
            field=models.IntegerField(default=0.0),
        ),
    ]