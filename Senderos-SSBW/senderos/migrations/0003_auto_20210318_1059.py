# Generated by Django 3.1.7 on 2021-03-18 09:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('senderos', '0002_excursion_fecha'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='excursion',
            name='fecha',
        ),
        migrations.AddField(
            model_name='excursion',
            name='likes',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='excursion',
            name='descripcion',
            field=models.TextField(max_length=1000),
        ),
        migrations.AlterField(
            model_name='excursion',
            name='nombre',
            field=models.CharField(max_length=100),
        ),
    ]
