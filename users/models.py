from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import ugettext_lazy as _
import random
from levels.models import RoyaltyGroup, CommissionGroup


class CustomUserManager(BaseUserManager):
    '''
    Define model manager for customized user model
    '''

    def _create_user(self, email, password=None, **extra_fields):
        '''
        Create and save a User with the given email and password
        '''
        if not email:
            raise ValueError('The email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)

        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        '''
        Create and save a superuser
        '''
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')

        return self._create_user(email, password, **extra_fields)


USER_TYPE_CHOICES = [
    (0, 'Admin'),
    (1, 'Artist'),
    (2, 'Interior Decorator'),
    (3, 'Firm')
]


class CustomUser(AbstractUser):
    username = models.CharField(max_length=100)
    email = models.EmailField(_('email address'), unique=True)
    phone = models.CharField(max_length=20, blank=True)
    type = models.IntegerField(
        choices=USER_TYPE_CHOICES, null=True, blank=True)
    profile_picture = models.ImageField(
        upload_to='profile_pictures', null=True, blank=True, default = 'default_dp.jpg')
    bio = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone', 'username', 'type']
    Unique_id = models.CharField(max_length=100, blank=True)
    object = CustomUserManager()

    def save(self, *args, **kwargs):
        self.Unique_id = self.first_name+self.last_name + \
            f'{random.randrange(10**5, 10**9)}'
        if not self.pk and not self.type:
            self.is_active = True
        super().save(*args, **kwargs)


class RandomPassword(models.Model):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, primary_key=True)
    random_string = models.CharField(max_length=36)

    def __str__(self):
        return self.user.email


class Code(models.Model):
    number = models.CharField(max_length=5, blank=True)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.number} - {self.user}"

    def save(self, *args, **kwargs):
        number_list = [x for x in range(10)]
        code_items = []
        for i in range(5):
            num = random.choice(number_list)
            code_items.append(num)
        code_string = "".join(str(items) for items in code_items)
        self.number = code_string
        super().save(*args, **kwargs)


class BaseUserType(models.Model):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, primary_key=True)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.user}"


class Firm(BaseUserType):
    members = models.ManyToManyField(CustomUser, related_name="members")
    platinum_commission_percent = models.DecimalField(
        max_digits=5, decimal_places=2, default=0)
    level = models.ForeignKey(
        CommissionGroup, on_delete=models.SET_NULL, null=True)
    reward_points = models.IntegerField(default=0)
    def get_commision_percent(self):
        if not self.platinum_commission_percent:
            return float(self.level.commission_percent)
        else:
            return float(self.platinum_commission_percent)
    def get_members(self):
        return self.members.all()


class Interior_Decorator(BaseUserType):
    platinum_commission_percent = models.DecimalField(
        max_digits=5, decimal_places=2, default=0)
    level = models.ForeignKey(
        CommissionGroup, on_delete=models.SET_NULL, null=True)
    coins = models.IntegerField(default=0)
    reward_points = models.IntegerField(default=0)
    def get_commision_percent(self):
        if not self.platinum_commission_percent:
            return float(self.level.commission_percent)
        else:
            return float(self.platinum_commission_percent)

    # def get_decorators_in_a_day(self):


class Artist(BaseUserType):
    level = models.ForeignKey(
        RoyaltyGroup, on_delete=models.SET_NULL, null=True)
    platinum_royalty_percent = models.DecimalField(
        max_digits=5, decimal_places=2, default=0)
    followers = models.ManyToManyField(Interior_Decorator, blank=True)
    earnings = models.FloatField(default=0)

    def get_royalty_percent(self):
        if not self.platinum_royalty_percent:
            return float(self.level.royalty_percent)
        else:
            return float(self.platinum_royalty_percent)

    def get_total_designs(self):
        return self.user.design_set.count()

    def get_followers_count(self):
        return self.followers.count()

    def get_total_views(self):
        total = 0
        for design in self.user.design_set.all():
            total += design.views

        return total

    def get_products_by_artist(self):
        design_list = self.design_set.all()

        product_list = []
        for design in design_list:
            product_list.append(design.product_set.all())

        return product_list


class OtpTable(models.Model):
    otp = models.CharField(max_length=10)
    timestamp = models.DateTimeField(auto_now_add=True) 

    def __str__(self):
        return f"{self.id} - {self.otp} - {self.timestamp}"