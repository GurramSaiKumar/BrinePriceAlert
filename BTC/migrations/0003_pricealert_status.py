# Generated by Django 4.2.1 on 2023-06-04 15:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BTC', '0002_alter_pricealert_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='pricealert',
            name='status',
            field=models.CharField(default='created', max_length=100),
        ),
    ]
