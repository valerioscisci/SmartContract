# Generated by Django 2.0.6 on 2019-08-17 21:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('smartrest', '0014_giornale_images'),
    ]

    operations = [
        migrations.RenameField(
            model_name='images',
            old_name='image',
            new_name='Image',
        ),
        migrations.AlterField(
            model_name='giornale',
            name='Meteo',
            field=models.CharField(blank=True, max_length=150),
        ),
    ]
