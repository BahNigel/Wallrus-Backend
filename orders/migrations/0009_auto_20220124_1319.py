# Generated by Django 3.2.3 on 2022-01-24 13:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0008_merge_0006_auto_20220119_1417_0007_alter_cart_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='purchaserequest',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
