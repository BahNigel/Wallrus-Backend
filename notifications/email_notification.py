from notifications.models import *
from users.models import *

from datetime import date, datetime, timedelta
from django.utils import timezone
from api.utils import send_mail

def daily_run():
    all_users = CustomUser.objects.filter(is_active=True)
    now = timezone.now()
    for user in all_users:
        if user.type ==1:
            send_artist(user)
        elif user.type == 2:
            send_decorator(user)
        else:
            pass


def send_artist(user):
    txt = ""
    now = timezone.now()
    artist = Artist.objects.get(user=user)
    setting = ArtistNotificationSettings.objects.get(user=artist)
    last_msg_time_1 = EmailNotificationHistory.objects.filter(user=user,notification_type = 'follower').order_by('-created_at').first().created_at
    if setting.follower_frequency == 2:
        start_date = now -timedelta(days=1)
        if start_date > last_msg_time_1:
            txt = get_Notification(user,"follower",txt)

    elif setting.follower_frequency == 3:
        start_date = now -timedelta(days=7)
        if start_date > last_msg_time_1:
            txt = get_Notification(user,"follower",txt)

    elif setting.follower_frequency == 4:
        start_date = now -timedelta(days=30)
        if start_date > last_msg_time_1:
            txt = get_Notification(user,"follower",txt)

    
    last_msg_time_2 = EmailNotificationHistory.objects.filter(user=user,notification_type = 'payment').order_by('-created_at').first().created_at
    if setting.payment_frequency == 2:
        start_date = now -timedelta(days=1)
        if start_date > last_msg_time_2:
            txt = get_Notification(user,"payment",txt)

    elif setting.payment_frequency == 3:
        start_date = now -timedelta(days=7)
        if start_date > last_msg_time_2:
            txt = get_Notification(user,"payment",txt)

    elif setting.payment_frequency == 4:
        start_date = now -timedelta(days=30)
        if start_date > last_msg_time_2:
            txt = get_Notification(user,"payment",txt)

    last_msg_time_3 = EmailNotificationHistory.objects.filter(user=user,notification_type = 'design_view').order_by('-created_at').first().created_at
    if setting.design_view_frequency == 2:
        start_date = now -timedelta(days=1)
        if start_date > last_msg_time_3:
            txt = get_Notification(user,"design_view",txt)

    elif setting.design_view_frequency == 3:
        start_date = now -timedelta(days=7)
        if start_date > last_msg_time_3:
            txt = get_Notification(user,"design_view",txt)

    elif setting.design_view_frequency == 4:
        start_date = now -timedelta(days=30)
        if start_date > last_msg_time_3:
            txt = get_Notification(user,"design_view",txt)

    last_msg_time_3 = EmailNotificationHistory.objects.filter(user=user,notification_type = 'design_favorite').order_by('-created_at').first().created_at
    if setting.design_favorite_frequency == 2:
        start_date = now -timedelta(days=1)
        if start_date > last_msg_time_3:
            txt = get_Notification(user,"design_favorite",txt)

    elif setting.design_favorite_frequency == 3:
        start_date = now -timedelta(days=7)
        if start_date > last_msg_time_3:
            txt = get_Notification(user,"design_favorite",txt)

    elif setting.design_favorite_frequency == 4:
        start_date = now -timedelta(days=30)
        if start_date > last_msg_time_3:
            txt = get_Notification(user,"design_favorite",txt)

    last_msg_time_3 = EmailNotificationHistory.objects.filter(user=user,notification_type = 'design_purchase').order_by('-created_at').first().created_at
    if setting.design_purchase_frequency == 2:
        start_date = now -timedelta(days=1)
        if start_date > last_msg_time_3:
            txt = get_Notification(user,"design_purchase",txt)

    elif setting.design_purchase_frequency == 3:
        start_date = now -timedelta(days=7)
        if start_date > last_msg_time_3:
            txt = get_Notification(user,"design_purchase",txt)

    elif setting.design_purchase_frequency == 4:
        start_date = now -timedelta(days=30)
        if start_date > last_msg_time_3:
            txt = get_Notification(user,"design_purchase",txt)

    if len(txt)>10:
        subject = "Wallrus Update"
        final_txt = txt
        to_email = str(user.email)
        data = {
            'email_subject':subject,
            'email_body':final_txt,
            'to_email':to_email
        }
        send_mail(data)


def send_decorator(user):
    txt = ""
    now = timezone.now()
    decorator = Interior_Decorator.objects.get(user=user)
    setting = InteriorDecoratorNotificationSettings.objects.get(user=decorator)
    last_msg_time_1 = EmailNotificationHistory.objects.filter(user=user,notification_type = 'purchase_commision_update').order_by('-created_at').first().created_at
    if setting.purchase_commision_update_frequency == 2:
        start_date = now -timedelta(days=1)
        if start_date > last_msg_time_1:
            txt = get_Notification(user,"purchase_commision_update",txt)

    elif setting.purchase_commision_update_frequency == 3:
        start_date = now -timedelta(days=7)
        if start_date > last_msg_time_1:
            txt = get_Notification(user,"purchase_commision_update",txt)

    elif setting.purchase_commision_update_frequency == 4:
        start_date = now -timedelta(days=30)
        if start_date > last_msg_time_1:
            txt = get_Notification(user,"purchase_commision_update",txt)
    
    last_msg_time_2 = EmailNotificationHistory.objects.filter(user=user,notification_type = 'followed_artist_new_design_update').order_by('-created_at').first().created_at
    if setting.followed_artist_new_design_update_frequency == 2:
        start_date = now -timedelta(days=1)
        if start_date > last_msg_time_2:
            txt = get_Notification(user,"followed_artist_new_design_update",txt)

    elif setting.followed_artist_new_design_update_frequency == 3:
        start_date = now -timedelta(days=7)
        if start_date > last_msg_time_2:
            txt = get_Notification(user,"followed_artist_new_design_update",txt)

    elif setting.followed_artist_new_design_update_frequency == 4:
        start_date = now -timedelta(days=30)
        if start_date > last_msg_time_2:
            txt = get_Notification(user,"followed_artist_new_design_update",txt)

    last_msg_time_3 = EmailNotificationHistory.objects.filter(user=user,notification_type = 'order_status').order_by('-created_at').first().created_at
    if setting.order_status_frequency == 2:
        start_date = now -timedelta(days=1)
        if start_date > last_msg_time_3:
            txt = get_Notification(user,"order_status",txt)

    elif setting.order_status_frequency == 3:
        start_date = now -timedelta(days=7)
        if start_date > last_msg_time_3:
            txt = get_Notification(user,"order_status",txt)

    elif setting.order_status_frequency == 4:
        start_date = now -timedelta(days=30)
        if start_date > last_msg_time_3:
            txt = get_Notification(user,"order_status",txt)

    last_msg_time_3 = EmailNotificationHistory.objects.filter(user=user,notification_type = 'new_artist_joined').order_by('-created_at').first().created_at
    if setting.new_artist_joined_frequency == 2:
        start_date = now -timedelta(days=1)
        if start_date > last_msg_time_3:
            txt = get_Notification(user,"new_artist_joined",txt)

    elif setting.new_artist_joined_frequency == 3:
        start_date = now -timedelta(days=7)
        if start_date > last_msg_time_3:
            txt = get_Notification(user,"new_artist_joined",txt)

    elif setting.new_artist_joined_frequency == 4:
        start_date = now -timedelta(days=30)
        if start_date > last_msg_time_3:
            txt = get_Notification(user,"new_artist_joined",txt)

    last_msg_time_3 = EmailNotificationHistory.objects.filter(user=user,notification_type = 'blog_news_event_notification').order_by('-created_at').first().created_at
    if setting.blog_news_event_notification_frequency == 2:
        start_date = now -timedelta(days=1)
        if start_date > last_msg_time_3:
            txt = get_Notification(user,"blog_news_event_notification",txt)

    elif setting.blog_news_event_notification_frequency == 3:
        start_date = now -timedelta(days=7)
        if start_date > last_msg_time_3:
            txt = get_Notification(user,"blog_news_event_notification",txt)

    elif setting.blog_news_event_notification_frequency == 4:
        start_date = now -timedelta(days=30)
        if start_date > last_msg_time_3:
            txt = get_Notification(user,"blog_news_event_notification",txt)

    if len(txt)>10:
        subject = "Wallrus Update"
        final_txt = txt
        to_email = str(user.email)
        data = {
            'email_subject':subject,
            'email_body':final_txt,
            'to_email':to_email
        }
        send_mail(data)

def get_Notification(user, type,txt):
    notifications = UserNotifications.objects.filter(user=user,notification_type=type, is_emailed = False)
    if notifications.count() > 0:
        txt = txt + f"{type} Updates-- \n"
        i = 1
        for notification in notifications:
            txt = txt + f"{notification.text} - {notification.created_at}"
            notification.is_emailed = True
            notification.save()

    nth_ins = EmailNotificationHistory(user=user,notification_type = type)
    nth_ins.save()