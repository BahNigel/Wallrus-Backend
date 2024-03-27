# Generated by Django 3.2.3 on 2022-02-26 16:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('levels', '0002_auto_20220205_1316'),
        ('users', '0008_interior_decorator_reward_points'),
    ]

    operations = [
        migrations.AddField(
            model_name='firm',
            name='level',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='levels.commissiongroup'),
        ),
        migrations.AddField(
            model_name='firm',
            name='platinum_commission_percent',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5),
        ),
    ]