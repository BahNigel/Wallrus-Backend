# Generated by Django 3.2.3 on 2022-01-17 07:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('user_details', '0003_alter_address_type'),
        ('orders', '0003_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='order_cost',
            field=models.FloatField(default=0),
        ),
        migrations.CreateModel(
            name='InstallationRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('phone', models.CharField(max_length=15)),
                ('email', models.CharField(max_length=50)),
                ('address', models.ForeignKey(limit_choices_to={'type': 5}, null=True, on_delete=django.db.models.deletion.SET_NULL, to='user_details.address')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
