# Generated by Django 5.2.1 on 2025-06-11 04:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='name',
            field=models.CharField(default='', max_length=255),
        ),
    ]
