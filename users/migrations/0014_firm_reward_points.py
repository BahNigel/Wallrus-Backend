# Generated by Django 3.2.3 on 2022-07-09 15:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0013_alter_customuser_profile_picture'),
    ]

    operations = [
        migrations.AddField(
            model_name='firm',
            name='reward_points',
            field=models.IntegerField(default=0),
        ),
    ]
