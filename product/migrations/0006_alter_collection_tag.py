# Generated by Django 3.2.3 on 2021-12-20 17:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0005_collection_updated_on'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collection',
            name='tag',
            field=models.ManyToManyField(blank=True, null=True, to='product.CollectionTag'),
        ),
    ]
