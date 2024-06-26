# Generated by Django 3.2.3 on 2021-12-10 16:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_shared', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField()),
                ('width', models.CharField(max_length=5)),
                ('height', models.CharField(max_length=5)),
            ],
        ),
        migrations.CreateModel(
            name='MeasurementRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('line1', models.TextField()),
                ('line2', models.TextField()),
                ('city', models.CharField(max_length=150)),
                ('state', models.CharField(max_length=150)),
                ('pincode', models.IntegerField()),
                ('date', models.DateField()),
                ('timeframe_of_measurement', models.CharField(max_length=255)),
                ('remarks', models.TextField()),
                ('site_image1', models.ImageField(upload_to='site_image/')),
                ('site_image2', models.ImageField(blank=True, null=True, upload_to='site_image/')),
                ('site_image3', models.ImageField(blank=True, null=True, upload_to='site_image/')),
                ('site_image4', models.ImageField(blank=True, null=True, upload_to='site_image/')),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='OrderStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('pending', 'Pending'), ('rejected', 'rejected'), ('confirmed', 'Confirmed'), ('shipped', 'Shipped'), ('delivered', 'Delivered')], max_length=10)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_status', to='orders.order')),
            ],
            options={
                'verbose_name_plural': 'Order Status',
            },
        ),
    ]
