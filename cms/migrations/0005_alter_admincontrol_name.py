# Generated by Django 3.2.3 on 2022-06-09 13:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0004_admincontrol'),
    ]

    operations = [
        migrations.AlterField(
            model_name='admincontrol',
            name='name',
            field=models.CharField(choices=[('admin_mail', 'Admin notification email'), ('main_email_password', 'Main email Password')], max_length=50, unique=True),
        ),
    ]
