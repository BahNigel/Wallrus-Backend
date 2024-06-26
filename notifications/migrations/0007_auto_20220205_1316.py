# Generated by Django 3.2.3 on 2022-02-05 13:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0006_auto_20220205_1028'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailnotificationhistory',
            name='notification_type',
            field=models.CharField(choices=[('order', 'Order'), ('follower', 'Follower'), ('product', 'product'), ('order-request', 'Order Request'), ('payment', 'Payment'), ('reward-point', 'Reward Points'), ('purchase-request', 'Purchase Request'), ('favourite', 'Favourite'), ('purchase_commision_update', 'purchase_commision_update'), ('followed_artist_new_design_update', 'followed_artist_new_design_update'), ('order_status', 'order_status'), ('new_artist_joined', 'new_artist_joined'), ('blog_news_event_notification', 'blog_news_event_notification'), ('design_view', 'design_view'), ('design_favorite', 'design_favorite'), ('decorator_level', 'Decorator Level')], max_length=50),
        ),
        migrations.AlterField(
            model_name='usernotifications',
            name='notification_type',
            field=models.CharField(choices=[('order', 'Order'), ('follower', 'Follower'), ('product', 'product'), ('order-request', 'Order Request'), ('payment', 'Payment'), ('reward-point', 'Reward Points'), ('purchase-request', 'Purchase Request'), ('favourite', 'Favourite'), ('purchase_commision_update', 'purchase_commision_update'), ('followed_artist_new_design_update', 'followed_artist_new_design_update'), ('order_status', 'order_status'), ('new_artist_joined', 'new_artist_joined'), ('blog_news_event_notification', 'blog_news_event_notification'), ('design_view', 'design_view'), ('design_favorite', 'design_favorite'), ('decorator_level', 'Decorator Level')], max_length=50),
        ),
    ]
