# Generated by Django 5.0.3 on 2024-09-19 07:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_alter_member_address_alter_member_city_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loan',
            name='rejection_reason',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]