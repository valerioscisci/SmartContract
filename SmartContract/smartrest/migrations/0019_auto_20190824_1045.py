# Generated by Django 2.0.6 on 2019-08-24 08:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('smartrest', '0018_auto_20190823_1351'),
    ]

    operations = [
        migrations.CreateModel(
            name='Transazione',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Descrizione', models.CharField(max_length=150)),
                ('Hash_Transazione', models.CharField(max_length=100)),
                ('Numero_Blocco', models.IntegerField()),
                ('Mittente', models.CharField(max_length=100)),
                ('Destinatario', models.CharField(max_length=100)),
            ],
        ),
        migrations.AlterField(
            model_name='contracts',
            name='Contract_Type',
            field=models.CharField(choices=[('Appalto', 'Appalto'), ('Valore', 'Valore'), ('Conforme', 'Conforme'), ('StringUtils', 'StringUtils')], max_length=50),
        ),
    ]
