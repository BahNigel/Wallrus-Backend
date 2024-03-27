from unicodedata import name
from django.db.models.signals import post_save
from django.dispatch import receiver

from users.models import CustomUser, Artist, RandomPassword, Interior_Decorator, Code, Firm
from levels.models import RoyaltyGroup, CommissionGroup
from notifications.models import ArtistNotificationSettings
from django.core.mail import send_mail
from backend import settings
from orders.models import Order, OrderStatus


@receiver(post_save, sender=CustomUser)
def at_ending(sender, instance, created, **kwargs):
    if created:
        print('Instance={0} created'.format(instance))
    elif instance.is_active == True:
        if instance.type == 1:
            if not Artist.objects.filter(user=instance).exists():
                Code.objects.create(user=instance)
                level = RoyaltyGroup.objects.filter(name=1).first()
                temp = Artist.objects.create(user=instance, level=level)
                ArtistNotificationSettings.objects.create(user=temp)
                print(
                    'Artist Model and NotificationSetting of {0} created'.format(temp))
                mail_subject = "Wallrus Account Approved"
                message = "Your Wallrus Artist account is activated now , log in here https://thewallruscompany.com/login"
                to_email = instance.email
                send_mail(
                    subject=mail_subject,
                    message=message,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[to_email],
                    fail_silently=True,
                )

        elif instance.type == 2:
            if not Interior_Decorator.objects.filter(user=instance).exists():
                Code.objects.create(user=instance)
                platinum_commission_percent = 0
                try:
                    level = CommissionGroup.objects.filter(name=1).first()
                    c = instance.members.all().count()
                    if c > 0:
                        firm = instance.members.all()[0]
                        level = firm.level
                        platinum_commission_percent = firm.platinum_commission_percent
                except:
                    pass
                temp = Interior_Decorator.objects.create(
                    user=instance, level=level, platinum_commission_percent = platinum_commission_percent)
                # ArtistNotificationSettings.objects.create(user=temp)
                print(
                    'Interior Decorator User Model of {0} created'.format(temp))

                mail_subject = "Wallrus Account Approved"
                message = "Your Wallrus Interior Decorator account is activated now , log in here https://thewallruscompany.com/login"
                to_email = instance.email
                send_mail(
                    subject=mail_subject,
                    message=message,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[to_email],
                    fail_silently=True,
                )
        elif instance.type == 3:
            if not Firm.objects.filter(user=instance).exists():
                Code.objects.create(user=instance)
                level = level = CommissionGroup.objects.filter(name=1).first()
                temp = Firm.objects.create(
                    user=instance, level=level)
                # ArtistNotificationSettings.objects.create(user=temp)
                print(
                    'Firm User Model of {0} created'.format(temp))


@receiver(post_save, sender=Order)
def at_ending(sender, instance, created, **kwargs):
    if created:
        print('Instance={0} created'.format(instance))

        OrderStatus.objects.create(order=instance, name='pending')
