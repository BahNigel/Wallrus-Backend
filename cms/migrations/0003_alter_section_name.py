# Generated by Django 3.2.3 on 2022-05-17 14:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0002_alter_section_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='section',
            name='name',
            field=models.CharField(choices=[('understand_wallrus_business_ecosystem', 'Understand The Wallrus Business Ecosystem'), ('artists_agreements', 'Artist’s Agreements'), ('uploading_managing_designs', 'Uploading and Managing your Designs'), ('understanding_media_art_working', 'Understanding the Media & Art working'), ('footer', 'Footer'), ('seller_agreement', 'Seller agreement'), ('return_exchange', 'Return and exchange'), ('privacy_policy', 'Privacy policy'), ('terms_of_use', 'Terms of use'), ('data_deletion', 'User data deletion instruction')], max_length=50, unique=True),
        ),
    ]
