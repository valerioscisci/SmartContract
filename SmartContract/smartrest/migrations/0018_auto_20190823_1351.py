# Generated by Django 2.0.6 on 2019-08-23 11:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('smartrest', '0017_lavoro_aliquota'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contracts',
            name='Contract_Type',
            field=models.CharField(choices=[('NO', 'No'), ('Si', 'Si')], max_length=50),
        ),
        migrations.AlterUniqueTogether(
            name='contracts',
            unique_together=set(),
        ),
        migrations.RemoveField(
            model_name='contracts',
            name='Contract_ID',
        ),
        migrations.RemoveField(
            model_name='contracts',
            name='Username',
        ),
    ]