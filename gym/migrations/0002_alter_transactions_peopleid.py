# Generated by Django 4.1.7 on 2023-11-11 00:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gym', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transactions',
            name='peopleId',
            field=models.ForeignKey(db_column='peopleId', on_delete=django.db.models.deletion.CASCADE, to='gym.people'),
        ),
    ]
