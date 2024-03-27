# Generated by Django 3.2.3 on 2021-12-10 16:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('orders', '0001_initial'),
        ('user_details', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='billing_address',
            field=models.ForeignKey(limit_choices_to={'type': 4}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='billing_address', to='user_details.address'),
        ),
        migrations.AddField(
            model_name='order',
            name='items',
            field=models.ManyToManyField(to='orders.Item'),
        ),
        migrations.AddField(
            model_name='order',
            name='shipping_address',
            field=models.ForeignKey(limit_choices_to={'type': 3}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='shipping_address', to='user_details.address'),
        ),
    ]
