from django.db import models
# from users.models import Interior_Decorator

from users.models import Artist, CustomUser, Interior_Decorator
# Create your models here.
from api.utils import send_mail
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from product.models import Product

frequency_status = [
    (1, 'Immediately'),
    (2, 'Daily'),
    (3, 'Weekly'),
    (4, 'Monthly')
]


class ArtistNotificationSettings(models.Model):
    user = models.OneToOneField(Artist, on_delete=models.CASCADE)
    follower_frequency = models.IntegerField(
        choices=frequency_status, default=1)
    payment_frequency = models.IntegerField(
        choices=frequency_status, default=1)
    design_view_frequency = models.IntegerField(
        choices=frequency_status, default=1)
    design_favorite_frequency = models.IntegerField(
        choices=frequency_status, default=1)
    design_purchase_frequency = models.IntegerField(
        choices=frequency_status, default=1)

    class Meta:
        verbose_name_plural = 'Artist notification settings'

    def __str__(self):
        return self.user.user.email

class InteriorDecoratorNotificationSettings(models.Model):
    user = models.OneToOneField(Interior_Decorator, on_delete=models.CASCADE)
    purchase_commision_update_frequency = models.IntegerField(
        choices=frequency_status, default=1)
    followed_artist_new_design_update_frequency = models.IntegerField(
        choices=frequency_status, default=1)
    order_status_frequency = models.IntegerField(
        choices=frequency_status, default=1)
    new_artist_joined_frequency = models.IntegerField(
        choices=frequency_status, default=1)
    blog_news_event_notification_frequency = models.IntegerField(
        choices=frequency_status, default=1)

    class Meta:
        verbose_name_plural = 'Interior Decorator notification settings'

    def __str__(self):
        return self.user.user.email

class NewsLetterSubscribers(models.Model):
    email = models.EmailField()
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.email

NOTIFICATION_TYPES = [
    ('order','Order'),
    ('follower', 'Follower'),
    ('product', 'product'),
    ('order-request', 'Order Request'),
    ('payment','Payment'),
    ('reward-point', 'Reward Points'),
    ('purchase-request', 'Purchase Request'),
    ('favourite', 'Favourite'),
    ('purchase_commision_update','purchase_commision_update'),
    ('followed_artist_new_design_update','followed_artist_new_design_update'),
    ('order_status','order_status'),
    ('new_artist_joined','new_artist_joined'),
    ('blog_news_event_notification', 'blog_news_event_notification'),
    ('design_view','design_view'),
    ('design_favorite','design_favorite'),
    ('decorator_level','Decorator Level')
]

class UserNotifications(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    notification_type = models.CharField(choices=NOTIFICATION_TYPES, max_length=50)
    text = models.CharField(max_length=100)
    creator = models.ForeignKey(CustomUser, blank=True, null=True, on_delete=models.SET_NULL, related_name='notification_creator')
    is_read = models.BooleanField(default=False)
    is_emailed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user}-{self.notification_type}-{self.text}"


class EmailNotificationHistory(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    notification_type = models.CharField(choices=NOTIFICATION_TYPES, max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

@receiver(post_save, sender=UserNotifications)
def check_immediate_notification(sender, instance,created,**kwargs):
    if created:
        try:
            immediate_notification(instance.user,instance)
        except:
            pass


def immediate_notification(user,notification):
    if user.type ==1:
        send_artist_immediate(user,notification)
    elif user.type == 2:
        send_decorator_immediate(user,notification)
    else:
        pass


def send_artist_immediate(user, notification):
    txt = ""
    artist = Artist.objects.get(user=user)
    setting = ArtistNotificationSettings.objects.get(user=artist)
    if setting.follower_frequency == 1 and notification.notification_type == 'follower':
        txt = notification.text
    
    if setting.payment_frequency == 1 and notification.notification_type == 'payment':
        txt = notification.text

    if setting.design_view_frequency == 1 and notification.notification_type == 'design_view':
        txt = notification.text

    if setting.design_favorite_frequency == 1 and notification.notification_type == 'design_favorite':
        txt = notification.text

    if setting.design_purchase_frequency == 1 and notification.notification_type == 'design_purchase':
        txt = notification.text

    if len(txt)>5:
        subject = "Wallrus Update"
        final_txt = txt
        to_email = str(user.email)
        data = {
            'email_subject':subject,
            'email_body':final_txt,
            'to_email':to_email
        }
        send_mail(data)


def send_decorator_immediate(user, notification):
    txt = ""
    decorator = Interior_Decorator.objects.get(user=user)
    setting = InteriorDecoratorNotificationSettings.objects.get(user=decorator)
    if setting.purchase_commision_update_frequency == 1 and notification.notification_type == 'purchase_commision':
        txt = notification.text
    
    if setting.followed_artist_new_design_update_frequency == 1 and notification.notification_type == 'followed_artist_new_design_update':
        txt = notification.text
    
    if setting.order_status_frequency == 1 and notification.notification_type == 'order_status':
        txt = notification.text
    
    if setting.new_artist_joined_frequency == 1 and notification.notification_type == 'new_artist_joined':
        txt = notification.text
    
    if setting.blog_news_event_notification_frequency == 1 and notification.notification_type == 'blog_news_event_notification':
        txt = notification.text
        
    if len(txt)>5:
        subject = "Wallrus Update"
        final_txt = txt
        to_email = str(user.email)
        data = {
            'email_subject':subject,
            'email_body':final_txt,
            'to_email':to_email
        }
        send_mail(data)

@receiver(pre_save, sender=Product)
def notify_followers(sender, instance,**kwargs):
    if instance.pk is None:
        artist = Artist.objects.get(user =instance.design.artist)
        followed_users = artist.followers.all()
        for decorator in followed_users:
            nt_ins = UserNotifications(user=decorator.user,creator=instance.design.artist, notification_type='followed_artist_new_design_update', text=f"{instance.design.artist.first_name} {instance.design.artist.last_name} just uploaded a new product")
            nt_ins.save()