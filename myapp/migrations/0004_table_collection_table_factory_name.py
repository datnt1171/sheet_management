# Generated by Django 5.1.6 on 2025-04-08 15:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0003_table_blueprint_table_panel'),
    ]

    operations = [
        migrations.AddField(
            model_name='table',
            name='collection',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='table',
            name='factory_name',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
