from email.mime import application
from django.db import models
from django.db.models import Sum
from django.forms import CharField
from django.utils.text import slugify
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from users.models import CustomUser, Artist

# Create your models here.

PRICING_CATEGORY_CHOICES = [
    ('category-1', 'Wallpapers, Wall & Furniture Decals, Glass Films'),
    ('category-2', 'Curtains'),
    ('category-3', 'Frames')
]

class Application(models.Model):
    name = models.CharField(max_length=50)
    slug = models.CharField(max_length=250, null=True, blank=True)
    pricing_category = models.CharField(choices=PRICING_CATEGORY_CHOICES, max_length=120, default='category-1')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        indexes = [models.Index(fields=['slug'])]

class Material(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    name = models.CharField(max_length=200,unique=True)
    unit_price = models.FloatField()
    unit_price_2 = models.FloatField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.application.name} {self.name}"

class Tag(models.Model):
    name = models.CharField(max_length=255)
    label = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        indexes = [models.Index(fields=['name'])]


class Product(models.Model):
    sku = models.BigAutoField(primary_key=True)
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    design = models.ForeignKey("designs.Design", on_delete=models.CASCADE)
    colorway = models.ForeignKey("designs.Colorway", on_delete=models.CASCADE)
    views = models.IntegerField(default=0)
    created_at = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    slug = models.CharField(max_length=250, null=True, blank=True)
    slug_tag = models.CharField(max_length=250, null=True, blank=True)
    favourited_by = models.ManyToManyField(CustomUser, limit_choices_to={
        'type': 2}, blank=True)

    def __str__(self):
        return f'{self.sku}-{self.design.name}.{self.colorway.name}.{self.application}'

    def get_slug(self):
        slug = ''
        try:
            for items in self.tags.all():
                slug += items.name+' '
        except:
            pass

        return slugify(slug)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(
                f'{self.design.pk} {self.design.name} {self.colorway.pk} {self.colorway.name} {self.application}')
        elif not self.slug_tag:
            self.slug_tag = self.get_slug()
        super().save(*args, **kwargs)

    def get_artist_name(self):
        return self.design.artist.first_name + ' ' + self.design.artist.last_name

    def get_artist_unique_id(self):
        return self.design.artist.Unique_id

    def get_artist_image(self):
        try :
            url =  self.design.artist.profile_picture.url
        except:
            url = ''
        return url

    def get_display_image(self):
        try:
            images = self.productimages_set.all().first().image.url
        except:
            images = ""
        return images

    def get_number_of_ratings(self):
        total = 0
        for review in self.reviews_set.all():
            total += review.rating
        return total

    def get_average_rating(self):
        total = 0
        for review in self.reviews_set.all():
            total += review.rating
        return "{:.1f}".format(total / self.reviews_set.count()) if self.reviews_set.count() else 0

    def get_royalty(self):
        artist_royalty_percent = self.design.artist.artist.get_royalty_percent()
        return artist_royalty_percent

    def get_is_approved(self):
        return self.design.is_approved

    def get_design_name(self):
        return self.design.name

    def get_colorway(self):
        return self.colorway.name

    def get_application(self):
        return self.application.name

    def get_total_sale(self):
        sale = self.item_set.all().exclude(order=None).count()
        return sale

    def get_total_revenue(self):
        rev = self.item_set.all().exclude(order=None).aggregate(Sum('price'))['price__sum']
        
        return rev

    class Meta:
        indexes = [models.Index(fields=['slug'])]
        unique_together = ['application', 'design', 'colorway']



class ProductImages(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/')

    class Meta:
        verbose_name_plural = 'Product Images'


class Reviews(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    reviewer = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)
    review = models.TextField()
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'Review by {self.reviewer.first_name} {self.reviewer.last_name} for {self.product.design.name}.{self.product.colorway.name}.{self.product.application}'

    def get_reviewer_name(self):
        return f'{self.reviewer.first_name} {self.reviewer.last_name}'

    def get_reviewer_picture(self):
        return f'{self.reviewer.profile_picture}'

    class Meta:
        verbose_name_plural = 'Reviews'

class CollectionTag(models.Model):
    name = models.CharField(max_length=1000)

    def __str__(self):
        return self.name
    
class Collection(models.Model):
    user = models.ForeignKey(CustomUser, limit_choices_to={
                             'type': 2}, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    products = models.ManyToManyField(Product)
    description = models.TextField()
    tag = models.ManyToManyField(CollectionTag, blank=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.pk} - {self.name} - {self.user}'
    
    def get_tag(self):
        tags = self.tag.all()
        tag_list = []
        for tag in tags:
            tag_list.append(tag.name)
        return tag_list

COUPON_CRITERIA_CHOICES = [
    ('percentage', 'Percentage'),
    ('substract', 'Substract'),
]

class Coupon(models.Model):
    user = models.ForeignKey(CustomUser, blank=True, null=True, on_delete=models.SET_NULL)
    code = models.CharField(max_length=20, unique=True)
    application_criteria = models.CharField(max_length=20, choices=COUPON_CRITERIA_CHOICES)
    off_value = models.FloatField()
    is_active = models.BooleanField(default=True)
    is_onetime = models.BooleanField(default=True)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code}-{self.application_criteria}-{self.off_value}-Active:{self.is_active}-One_time:{self.is_onetime}-Used:{self.is_used}"

