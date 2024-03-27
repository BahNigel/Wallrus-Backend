from unicodedata import name
from django.db import models
from django.db.models import Sum
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import date, datetime, timedelta

from levels.models import RoyaltyGroup, CommissionGroup
from notifications.models import UserNotifications

from user_details.models import Address
from product.models import Product, Material
from users.models import Artist, CustomUser, Interior_Decorator, Firm
# Create your models here.




class Cart(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    is_shared = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f'{self.user} is_Shared: {self.is_shared}'

    def get_total_price(self):
        return Item.objects.filter(cart=self).aggregate(Sum('price'))['price__sum']

STATUS_CHOICES = [
    ('cancelled', 'Cancelled'),
    ('pending', 'Pending'),
    ('rejected', 'rejected'),
    ('confirmed', 'Confirmed'),
    ('shipped', 'Shipped'),
    ('delivered', 'Delivered')
]


class Order(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    order_cost = models.FloatField(default=0)
    billing_address = models.ForeignKey(
        Address, on_delete=models.SET_NULL, null=True, related_name='billing_address')
    shipping_address = models.ForeignKey(
        Address, on_delete=models.SET_NULL, null=True, related_name='shipping_address')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.pk}-{self.user.first_name}-{self.created_at}"

@receiver(post_save, sender=Order)
def check_auto_upgrade(sender, instance,created,**kwargs):
    if created:
        for item in Item.objects.filter(order=instance):
            now = timezone.now()
            start_date = now -timedelta(days=30)
            artist_user = item.product.design.artist
            artist = Artist.objects.get(user=artist_user)
            decorator = Interior_Decorator.objects.get(user=instance.user)
            dec_order = Order.objects.filter(user = instance.user, created_at__gte=start_date)
            decorator_rev = dec_order.aggregate(Sum('order_cost'))['order_cost__sum']
            artist_rev = 0
            artist_orders = Order.objects.filter(items__product__design__artist = artist_user)
            for order in artist_orders:
                for item in order.items.all():
                    if item.product.design.artist.pk == artist_user.pk:
                        artist_rev += item.price
            dec_current_level = decorator.level.name
            art_current_level = artist.level.name
            dec_next_level = dec_current_level +1
            art_next_level = art_current_level + 1
            royalti_grp = RoyaltyGroup.objects.filter(name=art_next_level)
            commission_grp = CommissionGroup.objects.filter(name=dec_next_level)
            if commission_grp.exists():
                min_rev = commission_grp[0].min_revenue
                min_order = commission_grp[0].min_order
                if decorator_rev >= min_rev and dec_order.count() >= min_order:
                    decorator.level = commission_grp
                    decorator.save()
                    nt_ins = UserNotifications(user=artist.user, notification_type='decorator_level', text=f"Your Level is updated to {decorator.level.get_name_display()}")
                    nt_ins.save()

            if royalti_grp.exists():
                min_rev = royalti_grp[0].min_revenue
                min_design = royalti_grp[0].min_design
                if artist_rev >= min_rev and artist.get_total_designs() >= min_design:
                    artist.level = royalti_grp
                    artist.save()
                    nt_ins = UserNotifications(user=artist.user, notification_type='purchase_commision_update', text=f"Your Level is updated to {artist.level.get_name_display()}")
                    nt_ins.save()

class Item(models.Model):
    order = models.ForeignKey(Order, null=True, blank=True, on_delete=models.DO_NOTHING, default=None)
    cart = models.ForeignKey(Cart, null=True, blank=True, on_delete=models.DO_NOTHING, default=None)
    material = models.ForeignKey(Material, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    width = models.CharField(max_length=20)
    height = models.CharField(max_length=20)
    unit = models.CharField(max_length=20)
    price = models.IntegerField()
    
    def __str__(self) -> str:
        return f'{self.id},{self.product.design.name}.{self.product.colorway.name}.{self.product.application} Qty: {self.quantity} Price: {self.price}'

class OrderStatus(models.Model):
    order = models.ForeignKey(
        Order, related_name='order_status', on_delete=models.CASCADE)
    name = models.CharField(max_length=10, choices=STATUS_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Order Status'

    def __str__(self) -> str:
        return f"{self.order.id} - {self.name} {self.timestamp}"

@receiver(post_save, sender=OrderStatus)
def user_notify_users(sender, instance,created,**kwargs):
    if created:
        if instance.name != 'pending':
            nt_ins = UserNotifications(user=instance.order.user, notification_type='order', text=f"Your Order(id:{instance.order.pk}) status updated to: {instance.name}")
            nt_ins.save()


class MeasurementRequest(models.Model):
    name = models.CharField(max_length=255)
    line1 = models.TextField()
    line2 = models.TextField(null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    city = models.CharField(max_length=150)
    state = models.CharField(max_length=150)
    pincode = models.IntegerField()
    date = models.DateField()
    timeframe_of_measurement = models.CharField(max_length=255)
    remarks = models.TextField(null=True, blank=True)
    site_image1 = models.ImageField(upload_to='site_image/', null=True, blank=True)
    site_image2 = models.ImageField(upload_to='site_image/', null=True, blank=True)
    site_image3 = models.ImageField(upload_to='site_image/', null=True, blank=True)
    site_image4 = models.ImageField(upload_to='site_image/', null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.id} - {self.name}"

class InstallationRequest(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=15)
    email = models.CharField(max_length=50)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, limit_choices_to={'type': 5})

    def __str__(self):
        return f"{self.name} - {self.phone} - {self.email}"

class PurchaseRequest(models.Model):
    decorator = models.ForeignKey(Interior_Decorator, on_delete=models.CASCADE)
    firm = models.ForeignKey(Firm, on_delete=models.CASCADE)
    items = models.ManyToManyField(Item)
    price = models.IntegerField()
    client_name = models.CharField(max_length=100, null=True, blank=True)
    billing_address = models.ForeignKey(
        Address, on_delete=models.SET_NULL, null=True, limit_choices_to={'type': 4}, related_name='billing_address_request')
    shipping_address = models.ForeignKey(
        Address, on_delete=models.SET_NULL, null=True, limit_choices_to={'type': 3}, related_name='shipping_address_request')
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.decorator.user.first_name} - {self.price}"

class ClientDetails(models.Model):
    contact = models.CharField(max_length=100)
    decorator = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    address = models.ManyToManyField(Address)

    def __str__(self):
        return f"{self.contact} - {self.decorator}"

class ClientCart(models.Model):
    client = models.ForeignKey(ClientDetails, on_delete=models.CASCADE)
    description = models.CharField(max_length=200, null=True)
    items = models.ManyToManyField(Item)
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def get_total_price(self):
        return self.items.all().aggregate(Sum('price'))['price__sum']

    def __str__(self):
        return f"{self.client.contact} - {self.client.decorator} - {self.is_ordered}"


class Refund(models.Model):

    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    amount_refunded = models.FloatField(default=0)
    transaction_id = models.CharField(null=True, blank=True, max_length=50)
    created_at = models.DateTimeField(auto_now= True)
    is_refunded = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.order.id} - {self.order.user.first_name} {self.order.user.first_name} - cost: {self.order.order_cost}"