# Generated by Django 3.2.3 on 2022-07-09 15:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0021_auto_20220709_1408'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchaserequest',
            name='client_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
