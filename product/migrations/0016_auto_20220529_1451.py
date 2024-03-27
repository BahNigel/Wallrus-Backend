# Generated by Django 3.2.3 on 2022-05-29 14:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0015_alter_product_unique_together'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='cost',
        ),
        migrations.RemoveField(
            model_name='product',
            name='cost_2',
        ),
        migrations.RemoveField(
            model_name='product',
            name='material',
        ),
        migrations.RemoveField(
            model_name='product',
            name='tags',
        ),
        migrations.CreateModel(
            name='Material',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True)),
                ('unit_price', models.FloatField()),
                ('unit_price_2', models.FloatField()),
                ('application', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.application')),
            ],
        ),
    ]
