# Generated by Django 2.1.3 on 2018-11-20 07:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app01', '0006_auto_20181119_1627'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='deal_date',
            field=models.DateField(null=True),
        ),
    ]