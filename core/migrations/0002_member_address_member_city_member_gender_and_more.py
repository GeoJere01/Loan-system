# Generated by Django 5.0.3 on 2024-09-19 02:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='address',
            field=models.CharField(default=None, max_length=255),
        ),
        migrations.AddField(
            model_name='member',
            name='city',
            field=models.CharField(default=None, max_length=255),
        ),
        migrations.AddField(
            model_name='member',
            name='gender',
            field=models.CharField(choices=[('---Select---', '---Select---'), ('Male', 'Male'), ('Female', 'Female')], default='---Select---', max_length=50),
        ),
        migrations.AddField(
            model_name='member',
            name='id_number',
            field=models.CharField(default=None, max_length=255),
        ),
        migrations.AddField(
            model_name='member',
            name='id_type',
            field=models.CharField(choices=[('---Select---', '---Select---'), ('National ID', 'National ID'), ('Passport', 'Passport'), ('License', 'License')], default='---Select---', max_length=50),
        ),
        migrations.AddField(
            model_name='member',
            name='occupation',
            field=models.CharField(default=None, max_length=255),
        ),
        migrations.AddField(
            model_name='member',
            name='state',
            field=models.CharField(default=None, max_length=255),
        ),
    ]
