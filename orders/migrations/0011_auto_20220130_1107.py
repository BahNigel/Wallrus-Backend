# Generated by Django 3.2.3 on 2022-01-30 11:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0010_merge_20220125_0618'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='item',
            name='cart',
        ),
        migrations.AddField(
            model_name='cart',
            name='items',
            field=models.ManyToManyField(to='orders.Item'),
        ),
    ]
