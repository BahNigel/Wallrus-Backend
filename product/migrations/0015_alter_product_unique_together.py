# Generated by Django 3.2.3 on 2022-05-17 14:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('designs', '0005_designtag_is_approved'),
        ('product', '0014_auto_20220203_1046'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='product',
            unique_together={('application', 'design', 'colorway')},
        ),
    ]