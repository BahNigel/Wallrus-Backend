# Generated by Django 3.2.3 on 2022-01-22 13:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('designs', '0004_design_is_rejected'),
    ]

    operations = [
        migrations.AddField(
            model_name='designtag',
            name='is_approved',
            field=models.BooleanField(default=False),
        ),
    ]
