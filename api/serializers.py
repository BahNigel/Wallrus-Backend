
from dataclasses import fields
from pyexpat import model
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from django.db.models import Sum
from django.utils import timezone
from datetime import date, datetime, timedelta


from django.contrib.auth import password_validation
from users.models import CustomUser, Interior_Decorator, RandomPassword, Artist, Firm
from user_details.models import Address, BusinessDetail, BankDetail, CoinTransaction

from django.db.models import Count
from .utils import get_tags_by_label, random_password_generator, Encrypt_and_Decrypt
from designs.models import Design, DesignTag, Colorway, Customization, UploadOwnDesign
from notifications.models import ArtistNotificationSettings, InteriorDecoratorNotificationSettings

from product.models import Application, Product, ProductImages, Reviews, Tag, Collection, Material
from posts.models import Post
from orders.models import Order, Item, OrderStatus, MeasurementRequest, PurchaseRequest
from levels.models import CommissionGroup, Group

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework.exceptions import APIException

class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        from django.core.files.base import ContentFile
        import base64
        import six
        import uuid

        # Check if this is a base64 string
        if isinstance(data, six.string_types):
            # Check if the base64 string is in the "data:" format
            if 'data:' in data and ';base64,' in data:
                # Break out the header from the base64 content
                header, data = data.split(';base64,')

            # Try to decode the file. Return validation error if it fails.
            try:
                decoded_file = base64.b64decode(data)
            except TypeError:
                self.fail('invalid_image')

            # Generate file name:
            # 12 characters are more than enough.
            file_name = str(uuid.uuid4())[:12]
            # Get the file name extension:
            file_extension = self.get_file_extension(file_name, decoded_file)

            complete_file_name = "%s.%s" % (file_name, file_extension, )

            data = ContentFile(decoded_file, name=complete_file_name)

        return super(Base64ImageField, self).to_internal_value(data)

    def get_file_extension(self, file_name, decoded_file):
        import imghdr

        extension = imghdr.what(file_name, decoded_file)
        extension = "jpg" if extension == "jpeg" else extension

        return extension


class RegisterUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True
    )
    profile_picture = Base64ImageField(
        max_length=None, use_url=True,
    )

    class Meta:
        model = CustomUser
        fields = ('email', 'password', 'type',
                  'profile_picture', 'first_name', 'last_name', 'username',  'phone', 'bio')

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        random_string = ''

        if password:
            instance.set_password(password)
        else:
            random_string = random_password_generator()
            instance.set_password(random_string)
        instance.save()

        if random_string:
            obj = RandomPassword.objects.create(
                user=instance, random_string=random_string)
            obj.save()

        return instance

class AddUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True
    )
    profile_picture = Base64ImageField(
        max_length=None, use_url=True, required=False
    )

    class Meta:
        model = CustomUser
        fields = ('email', 'password', 'type',
                  'profile_picture', 'first_name', 'last_name', 'username',  'phone', 'bio')

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        random_string = ''

        if password:
            instance.set_password(password)
        else:
            random_string = random_password_generator()
            instance.set_password(random_string)
        instance.save()

        if random_string:
            obj = RandomPassword.objects.create(
                user=instance, random_string=random_string)
            obj.save()

        return instance


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ('pk','user', 'type', 'line1', 'line2', 'city', 'state', 'pincode')


class BusinessDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessDetail
        fields = ('user', 'pan_card_number', 'brand_name',
                  'gst_number', 'phone', 'email')

    def create(self, validated_data):
        instance = self.Meta.model(**validated_data)
        pan_card_number = instance.pan_card_number
        gst_number = instance.gst_number
        if pan_card_number and gst_number:
            en = Encrypt_and_Decrypt()
            instance.pan_card_number = en.encrypt(pan_card_number)
            instance.gst_number = en.encrypt(gst_number)
            del en
        instance.save()
        return instance


class BankDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankDetail
        fields = ('user', 'account_number', 'name',
                  'branch', 'ifsc_code', 'swift_code')

    def create(self, validated_data):
        instance = self.Meta.model(**validated_data)
        account_number = instance.account_number
        swift_code = instance.swift_code
        if account_number and swift_code:
            en = Encrypt_and_Decrypt()
            instance.account_number = en.encrypt(account_number)
            instance.swift_code = en.encrypt(swift_code)
            del en
        instance.save()
        return instance


class ApplistSerializer(serializers.ModelSerializer):
    product_count = serializers.SerializerMethodField()

    def get_product_count(self, obj):
        return Product.objects.filter(application=obj).count()
    class Meta:
        model = Application
        fields = ['name', 'slug','product_count']


class ChangePasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['password']

    def validate_password(self, value):
        password_validation.validate_password(value, self.instance)
        return value

class SearchUserSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()

    def get_type(self, obj):
        return obj.get_type_display()

    class Meta:
        model = CustomUser
        fields = ['pk','profile_picture', 'first_name', 'last_name',
                  'email', 'phone', 'username', 'type','Unique_id']

class SearchPostSerializer(serializers.ModelSerializer):

    class Meta:
        model= Post
        fields = ['title', 'category', 'image', 'slug', 'created_at']



class SocialUserDetailsSerializer(serializers.ModelSerializer):
    type = serializers.CharField(source='get_type_display')

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'type', 'first_name', 'last_name']

##################################################### ARTIST SERIALIZERS ###################################################

class ArtistSnippetSerializer(serializers.ModelSerializer):
    level = serializers.SerializerMethodField()
    followers = serializers.SerializerMethodField()
    total_designs = serializers.SerializerMethodField()
    views = serializers.SerializerMethodField()
    member_since = serializers.SerializerMethodField()
    favourite = serializers.SerializerMethodField()
    sales = serializers.SerializerMethodField()
    earnings = serializers.SerializerMethodField()

    def get_level(self, obj):
        return obj.artist.level.get_name_display()

    def get_followers(self, obj):
        return obj.artist.followers.count()

    def get_total_designs(self, obj):
        return obj.artist.get_total_designs()

    def get_views(self, obj):
        return Product.objects.filter(design__artist = obj).aggregate(Sum('views'))['views__sum']

    def get_member_since(self, obj):
        return obj.date_joined.date()

    def get_favourite(self,obj):
        count = 0
        products = Product.objects.filter(design__artist = obj)
        for product in products:
            count += product.favourited_by.all().count()
        return count
    
    def get_sales(self,obj):
        sales = Item.objects.filter(product__design__artist=obj).exclude(order=None).exclude(order__order_status__name = 'pending').exclude(order__order_status__name = 'rejected').count()
        if sales:
            return sales
        else:
            return 0

    def get_earnings(self,obj):
        # rev = Item.objects.filter(product__design__artist=obj).exclude(order=None).exclude(order__order_status__name = 'pending').exclude(order__order_status__name = 'rejected').aggregate(Sum('price'))['price__sum']
        # rev = Order.objects.filter(items_set__product__design__artist=obj).exclude(order_status__name = 'pending').exclude(order_status__name = 'rejected').aggregate(Sum('order_cost'))['order_cost__sum']
        earnings = Artist.objects.get(user=obj).earnings
        if earnings:
            return "%.2f"%earnings
        else:
            return 0

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name',
                  'profile_picture', 'sales','earnings',
                  'level', 'bio', 'total_designs', 'followers', 'views', 'member_since', 'Unique_id', 'favourite', 'email']


class DesignTagSerializer(serializers.ModelSerializer):
    tags = serializers.SerializerMethodField()

    def get_tags(self, obj):
        return get_tags_by_label(DesignTag, obj['label'])

    class Meta:
        model = DesignTag
        fields = ['label', 'tags']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        for tag in self.initial_data['tags']:
            self.instance.name = tag['name']

        self.instance.save()
        return self.instance


class ArtistNotificationSettingsSerailizer(serializers.ModelSerializer):
    follower_frequency = serializers.SerializerMethodField()
    payment_frequency = serializers.SerializerMethodField()
    design_view_frequency = serializers.SerializerMethodField()
    design_favorite_frequency = serializers.SerializerMethodField()
    design_purchase_frequency = serializers.SerializerMethodField()

    class Meta:
        model = ArtistNotificationSettings
        fields = ['follower_frequency', 'payment_frequency',
                  'design_view_frequency',
                  'design_favorite_frequency',
                  'design_purchase_frequency']

    def get_follower_frequency(self, obj):
        return obj.get_follower_frequency_display()

    def get_payment_frequency(self, obj):
        return obj.get_payment_frequency_display()

    def get_design_view_frequency(self, obj):
        return obj.get_design_view_frequency_display()

    def get_design_favorite_frequency(self, obj):
        return obj.get_design_favorite_frequency_display()

    def get_design_purchase_frequency(self, obj):
        return obj.get_design_purchase_frequency_display()

    def save(self, **kwargs):
        super().save(**kwargs)

        frequency_status = ['Immediately', 'Daily', 'Weekly', 'Monthly']

        self.instance.follower_frequency = frequency_status.index(
            self.initial_data['follower_frequency']) + 1

        self.instance.payment_frequency = frequency_status.index(
            self.initial_data['payment_frequency']) + 1

        self.instance.design_view_frequency = frequency_status.index(
            self.initial_data['design_view_frequency']) + 1

        self.instance.design_favorite_frequency = frequency_status.index(
            self.initial_data['design_favorite_frequency']) + 1

        self.instance.design_purchase_frequency = frequency_status.index(
            self.initial_data['design_purchase_frequency']) + 1

        self.instance.save()

        return self.instance

class InteriorDecoratorNotificationSettingsSerailizer(serializers.ModelSerializer):
    purchase_commision_update_frequency = serializers.SerializerMethodField()
    followed_artist_new_design_update_frequency = serializers.SerializerMethodField()
    order_status_frequency = serializers.SerializerMethodField()
    new_artist_joined_frequency = serializers.SerializerMethodField()
    blog_news_event_notification_frequency = serializers.SerializerMethodField()

    class Meta:
        model = InteriorDecoratorNotificationSettings
        fields = ['purchase_commision_update_frequency', 
                  'followed_artist_new_design_update_frequency',
                  'order_status_frequency',
                  'new_artist_joined_frequency',
                  'blog_news_event_notification_frequency']
    def get_purchase_commision_update_frequency(self, obj):
        return obj.get_purchase_commision_update_frequency_display()

    def get_followed_artist_new_design_update_frequency(self, obj):
        return obj.get_followed_artist_new_design_update_frequency_display()

    def get_order_status_frequency(self, obj):
        return obj.get_order_status_frequency_display()

    def get_new_artist_joined_frequency(self, obj):
        return obj.get_new_artist_joined_frequency_display()

    def get_blog_news_event_notification_frequency(self, obj):
        return obj.get_blog_news_event_notification_frequency_display()

    def save(self, **kwargs):
        super().save(**kwargs)

        frequency_status = ['Immediately', 'Daily', 'Weekly', 'Monthly']

        self.instance.purchase_commision_update_frequency = frequency_status.index(
            self.initial_data['purchase_commision_update_frequency']) + 1

        self.instance.followed_artist_new_design_update_frequency = frequency_status.index(
            self.initial_data['followed_artist_new_design_update_frequency']) + 1

        self.instance.order_status_frequency = frequency_status.index(
            self.initial_data['order_status_frequency']) + 1

        self.instance.new_artist_joined_frequency = frequency_status.index(
            self.initial_data['new_artist_joined_frequency']) + 1

        self.instance.blog_news_event_notification_frequency = frequency_status.index(
            self.initial_data['blog_news_event_notification_frequency']) + 1

        self.instance.save()

        return self.instance




class UploadDesignTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = DesignTag
        fields = ['name', 'label']


class ColowaySerializer(serializers.ModelSerializer):

    class Meta:
        model = Colorway
        fields = ['design', 'name', 'image_url']

    def create(self, validated_data):
        instance = self.Meta.model(**validated_data)

        instance.save()

        return instance

class UnderReviewSerializer(serializers.ModelSerializer):
    applications = ApplistSerializer(many=True)
    colorway_set = ColowaySerializer(many=True)
    
    class Meta:
        model = Design
        fields = ['name', 'applications', 'colorway_set','created_at']

class UploadDesignSerializer(serializers.ModelSerializer):
    applications = ApplistSerializer(many=True)

    class Meta:
        model = Design
        fields = ['artist', 'name', 'is_customizable', 'applications']

    def create(self, validated_data):
        apps = validated_data.pop('applications')
        instance = self.Meta.model(**validated_data)
        instance.save()

        for app in apps:
            app_obj = Application.objects.get(**app)
            instance.applications.add(app_obj)

        instance.save()
        return instance


class UserTypeSerializer(serializers.ModelSerializer):
    type = serializers.CharField(source='get_type_display')

    class Meta:
        model = CustomUser
        fields = ['type']

class ArtistDesignSerializer(serializers.ModelSerializer):
    product_image = serializers.SerializerMethodField()
    is_favourite = serializers.SerializerMethodField(allow_null=True)
    is_approved = serializers.SerializerMethodField()
    revenue = serializers.SerializerMethodField()
    sales = serializers.SerializerMethodField()
    views = serializers.SerializerMethodField()
    design_name = serializers.SerializerMethodField()
    colorway = serializers.SerializerMethodField()
    application = serializers.SerializerMethodField()
    favourite_count = serializers.SerializerMethodField()

    def get_product_image(self,obj):
        return obj.get_display_image()

    def get_is_favourite(self,obj):
        fav = Product.objects.filter(sku = obj.sku, favourited_by__email=self.context['request'].user, favourited_by__is_active=True).exists()
        return fav
    
    def get_is_approved(self, obj):
        return obj.get_is_approved()

    def get_revenue(self, obj):
        return obj.get_total_revenue()

    def get_sales(self, obj):
        return obj.get_total_sale()

    def get_views(self, obj):
        return obj.views

    def get_design_name(self, obj):
        return obj.get_design_name()

    def get_colorway(self, obj):
        return obj.get_colorway()

    def get_application(self, obj):
        return obj.get_application()

    def get_favourite_count(self,obj):
        return obj.favourited_by.all().count()

    class Meta:
        model = Product
        fields = [
            'sku', 'design_name', 'colorway', 'application', 'product_image', 'is_favourite', 'is_approved', 'revenue', 'sales', 'views' ,'favourite_count', 'slug'
        ]

class ArtistDetailsSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    followers_count = serializers.SerializerMethodField()
    bio = serializers.SerializerMethodField()
    profile_pic = serializers.SerializerMethodField()
    no_of_designs = serializers.SerializerMethodField()
    level = serializers.SerializerMethodField()
    user_since = serializers.SerializerMethodField()
    is_followed = serializers.SerializerMethodField()

    def get_email(self,obj):
        return obj.user.email

    def get_full_name(self,obj):
        first_name = obj.user.first_name
        last_name = obj.user.last_name
        full_name = first_name + " " + last_name
        return full_name

    def get_followers_count(self,obj):
        return obj.get_followers_count()

    def get_bio(self, obj):
        return obj.user.bio

    def get_profile_pic(self, obj):
        try:
            img = obj.user.profile_picture.url
        except:
            img = " "
        return img

    def get_no_of_designs(self,obj):
        return obj.get_total_designs()

    def get_level(self, obj):
        return obj.level.get_name_display()

    def get_user_since(self,obj):
        return obj.user.date_joined

    def get_is_followed(self,obj):
        follow_status = Artist.objects.filter(user = obj, followers__user = self.context['request'].user).exists()
        return follow_status

    class Meta:
        model = Artist
        fields = ['email', 'full_name', 'followers_count', 'bio', 'profile_pic', 'no_of_designs','level', 'user_since', 'is_followed']


############################################################## SHOP SERIALIZERS #######################################################

class FilterSerializer(serializers.ModelSerializer):
    tags = serializers.SerializerMethodField()

    def get_tags(self, obj):
        return get_tags_by_label(DesignTag, obj['label'])

    class Meta:
        model = DesignTag
        fields = ['label', 'tags']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = DesignTag
        fields = ['name', 'label']


class ProductImagesSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()

    def get_images(self, obj):
        return obj.image.url

    class Meta:
        model = ProductImages
        fields = ['images']


class MaterialSerializer(serializers.ModelSerializer):

    class Meta:
        model = Material
        fields = "__all__"


class ProductListSerializer(serializers.ModelSerializer):
    productimage = serializers.SerializerMethodField()
    design_name = serializers.SerializerMethodField()
    colorway_name = serializers.SerializerMethodField()
    application = serializers.SerializerMethodField()
    artist = serializers.SerializerMethodField()
    artist_image = serializers.SerializerMethodField(allow_null=True)
    is_favourite = serializers.SerializerMethodField(allow_null=True)
    artist_unique_id = serializers.SerializerMethodField(allow_null=True)

    # def get_product_image(self, obj):
    #     return obj.get_display_image()

    def get_design_name(self, obj):
        return obj.design.name

    def get_colorway_name(self, obj):
        return obj.colorway.name

    def get_application(self, obj):
        return obj.application.name

    def get_artist(self, obj):
        return obj.get_artist_name()
    
    def get_artist_image(self, obj):
        return obj.get_artist_image()

    def get_is_favourite(self,obj):
        fav = Product.objects.filter(sku = obj.sku, favourited_by__email=self.context['request'].user, favourited_by__is_active=True).exists()
        return fav

    def get_productimage(self,obj):
        return obj.get_display_image()

    def get_artist_unique_id(self, obj):
        return obj.get_artist_unique_id()

    class Meta:
        model = Product
        fields = ['sku', 'artist', 'design_name', 'artist_unique_id',
                  'application', 'colorway_name', 'productimage', 'slug', 'artist_image', 'is_favourite']


class ReviewsSerializer(serializers.ModelSerializer):
    reviewer = serializers.SerializerMethodField()
    profile_picture = serializers.SerializerMethodField()

    def get_reviewer(self, obj):
        return obj.get_reviewer_name()

    def get_profile_picture(self, obj):
        return "/media/"+obj.get_reviewer_picture()

    class Meta:
        model = Reviews
        fields = ['reviewer', 'profile_picture', 'rating',
                  'review', 'created_at']


class ProductDetailSerializer(serializers.ModelSerializer):
    ratings = serializers.SerializerMethodField()
    number_of_ratings = serializers.SerializerMethodField()
    productimages_set = ProductImagesSerializer(many=True)
    application = serializers.SerializerMethodField()
    application_slug = serializers.SerializerMethodField()
    colorway = serializers.SerializerMethodField()
    artist = serializers.SerializerMethodField()
    artist_unique_id = serializers.SerializerMethodField()
    reviews_set = ReviewsSerializer(many=True)
    design_name = serializers.SerializerMethodField()
    is_favourite = serializers.SerializerMethodField(allow_null=True)
    pricing_category = serializers.SerializerMethodField()
    royalty_percent = serializers.SerializerMethodField()

    def  get_royalty_percent(self,obj):
        return obj.get_royalty()

    def get_ratings(self, obj):
        return obj.get_average_rating()

    def get_number_of_ratings(self, obj):
        return obj.get_number_of_ratings()

    def get_artist(self, obj):
        return obj.get_artist_name()

    def get_artist_unique_id(self, obj):
        return obj.get_artist_unique_id()

    def get_application(self, obj):
        return obj.application.name

    def get_application_slug(self, obj):
        return obj.application.slug

    def get_colorway(self, obj):
        return obj.colorway.name

    def get_design_name(self, obj):
        return obj.design.name

    def get_is_favourite(self,obj):
        fav = Product.objects.filter(sku = obj.sku, favourited_by__email=self.context['request'].user, favourited_by__is_active=True).exists()
        return fav

    def get_pricing_category(self,obj):
        return obj.application.pricing_category

    class Meta:
        model = Product
        fields = ['sku', 'application', 'application_slug', 'colorway', 'design_name', 'productimages_set',
                  'artist', 'artist_unique_id', 'ratings', 'number_of_ratings', 'reviews_set', 'is_favourite', 'pricing_category', 'royalty_percent']


class ProfileImageSerializer(serializers.ModelSerializer):
    profile_picture = Base64ImageField(
        max_length=None, use_url=True,
    )

    class Meta:
        model = CustomUser
        fields = ['profile_picture']


class FeaturedArtistListSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    user = ProfileImageSerializer()
    no_of_designs = serializers.SerializerMethodField()
    no_of_followers = serializers.SerializerMethodField()

    class Meta:
        model = Artist
        fields = ['full_name', 'no_of_followers', 'no_of_designs', 'user']

    def get_full_name(self, obj):
        return obj.user.first_name+' '+obj.user.last_name

    def get_no_of_followers(self, obj):
        return obj.followers.count()

    def get_no_of_designs(self, obj):
        return Design.objects.filter(artist=obj.user).count()


class DesignListSerializer(serializers.ModelSerializer):
    designer = serializers.SerializerMethodField()

    class Meta:
        model = Design
        fields = ['designer']

    def get_designer(self, obj):
        return obj.get_artist_name()


# class ArtistListStatusSerializer(serializers.ModelSerializer):
#     full_name = serializers.SerializerMethodField()
#     status = serializers.SerializerMethodField()
#     profile_picture =ProductImagesSerializer(many=True)
#     class Meta:
#         model = Artist
#         fields = ['full_name','status','profile_picture']
#     def get_full_name(self,obj):
#         return obj.user.first_name+' '+obj.user.last_name

#     def get_status(self,obj):
#         # name = CustomUser.objects.get(email=self.context['request'].user)
#         temp = obj.followers.filter(user__email=self.context['request'].user).exists()
#         return temp


class ArtistListStatusSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    followers = serializers.SerializerMethodField()
    Unique_id = serializers.SerializerMethodField()
    Designs = serializers.SerializerMethodField()
    user = ProfileImageSerializer()
    design_images = serializers.SerializerMethodField()


    class Meta:
        model = Artist
        fields = ['full_name', 'followers',
                  'Designs', 'status', 'user', 'Unique_id', 'design_images']

    def get_full_name(self, obj):
        return obj.user.first_name+' '+obj.user.last_name

    def get_status(self, obj):
        # name = CustomUser.objects.get(email=self.context['request'].user)
        temp = Artist.objects.filter(
            followers__user__email=self.context['request'].user, pk=obj.user.id).exists()
        return temp

    def get_followers(self, obj):
        return obj.followers.count()

    def get_Unique_id(self, obj):
        return obj.user.Unique_id

    def get_Designs(self, obj):
        return Design.objects.filter(artist=obj.user, is_approved=True).count()

    def get_design_images(self, obj):
        products = Product.objects.filter(design__artist=obj.user)
        images = [product.get_display_image() for product in products]
        return images[0:3]

class DesignSerializer(serializers.ModelSerializer):
    designer_name = serializers.SerializerMethodField()
    productimages_set = ProductImagesSerializer(many=True)
    designer_picture = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['designer_name', 'productimages_set', 'designer_picture']

    def get_designer_name(self, obj):
        return obj.get_artist_name()

    def get_designer_picture(self, obj):
        if obj.design.artist.profile_picture:
            return obj.design.artist.profile_picture.url
        else:
            return "/media/profile_pictures/unknown.png"


class ProductReviewSerializer(serializers.ModelSerializer):
    reviewer = serializers.SerializerMethodField()
    profile_picture = serializers.SerializerMethodField()
    product_slug = serializers.SerializerMethodField()

    def get_reviewer(self, obj):
        return obj.get_reviewer_name()

    def get_profile_picture(self, obj):
        return "/media/"+obj.get_reviewer_picture()

    def get_product_slug(self, obj):
        return obj.product.slug
    class Meta:
        model = Reviews
        fields = ['reviewer', 'profile_picture', 'rating',
                  'review', 'created_at', 'product_slug']


class SearchProductListSerializer(serializers.ModelSerializer):
    productimage = serializers.SerializerMethodField()
    design_name = serializers.SerializerMethodField()
    colorway_name = serializers.SerializerMethodField()
    application = serializers.SerializerMethodField()
    artist = serializers.SerializerMethodField()

    # def get_product_image(self, obj):
    #     return obj.get_display_image()

    def get_design_name(self, obj):
        return obj.design.name

    def get_colorway_name(self, obj):
        return obj.colorway.name

    def get_application(self, obj):
        return obj.application.name

    def get_artist(self, obj):
        return obj.get_artist_name()

    def get_productimage(self,obj):
        return obj.get_display_image()

    class Meta:
        model = Product
        fields = ['sku', 'artist', 'design_name',
                  'application', 'colorway_name', 'productimage', 'slug']

##################################################### FIRM SERIALIZERS ###################################################


class FirmUserListSerializer(serializers.ModelSerializer):
    commission = serializers.SerializerMethodField()
    total_sale = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    is_verified = serializers.SerializerMethodField()
    level = serializers.SerializerMethodField()

    def get_commission(self, obj):
        try:
            decorator = Interior_Decorator.objects.get(user=obj)
            return decorator.get_commision_percent()
        except Exception as e:
            print(e)
            return None

    def get_total_sale(self, obj):
        items = Item.objects.filter(order__user=obj)
        order_cost = 0
        for item in items.all():
            order_cost += item.price
        return order_cost

    def get_first_name(self, obj):
        return obj.first_name

    def get_last_name(self, obj):
        return obj.last_name

    def get_username(self, obj):
        return obj.username

    def get_is_verified(self, obj):
        return obj.is_active

    def get_level(self, obj):
        try:
            decorator = Interior_Decorator.objects.get(user=obj)
            return decorator.level.get_name_display()
        except:
            return None

    class Meta:
        model = CustomUser
        fields = ['pk', 'profile_picture','first_name',
                  'last_name', 'username', 'is_verified', 'level',
                  'commission', 'total_sale']


class FirmOrderSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()

    def get_status(self, obj):
        order_status = obj.order_status.order_by('-id').first()
        if order_status:
            return order_status.name
        else:
            return None

    def get_user(self, obj):
        return obj.user.first_name + ' ' + obj.user.last_name

    def get_created_at(self, obj):
        return obj.created_at.strftime("%d %B %Y %I:%M%p")

    class Meta:
        model = Order
        fields = ['id', 'user', 'created_at', 'status']


class FirmUserSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    business_details = BusinessDetailSerializer()
    bank_details = BankDetailSerializer()

    def get_type(self, obj):
        return obj.get_type_display()

    class Meta:
        model = CustomUser
        fields = ['profile_picture', 'first_name', 'last_name',
                  'email', 'phone', 'username', 'type', 'business_details', 'bank_details']


class FirmSalesGraphSerializer(serializers.ModelSerializer):
    order_cost = serializers.SerializerMethodField()

    def get_order_cost(self, obj):
        order_cost = 0
        for item in obj.items.all():
            order_cost += item.product.cost * item.quantity
        return order_cost

    class Meta:
        model = Order
        fields = ['created_at', 'order_cost']


class IntDecoratorDetailSerializer(serializers.ModelSerializer):
    level = serializers.SerializerMethodField()
    business_details = BusinessDetailSerializer()
    bank_details = BankDetailSerializer()

    def get_level(self, obj):
        decorator = get_object_or_404(Interior_Decorator, user=obj.id)
        return decorator.level.get_name_display()

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email',
                  'phone', 'level', 'business_details', 'bank_details']


class CardDetailSerializer(serializers.ModelSerializer):
    total_decorators = serializers.SerializerMethodField()
    total_expense = serializers.SerializerMethodField()
    total_request = serializers.SerializerMethodField()

    def get_total_decorators(self, obj):
        members = obj.members.all().count()
        return members

    def get_total_request(self, obj):
        return PurchaseRequest.objects.filter(firm = obj).count()

    def get_total_expense(self, obj):
        orders = Order.objects.filter(user=obj.user)
        order_cost = 0
        for order in orders:
            for item in order.items.all():
                order_cost += item.price
        return order_cost

    class Meta:
        model = Firm
        fields = ['total_decorators', 'total_expense','total_request']

class ItemSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    cost = serializers.SerializerMethodField()
    material = serializers.SerializerMethodField()

    def get_material(self, obj):
        try:
            mat = obj.material.name
        except:
            mat = ""
        
        return mat

    def get_image(self, obj):
        return obj.product.get_display_image()

    def get_name(self, obj):
        return f'{obj.product.design.name}.{obj.product.colorway.name}.{obj.product.application}'

    def get_cost(self, obj):
        return obj.price

    class Meta:
        model = Item
        fields = ['image', 'name', 'cost', 'quantity', 'width', 'height' , 'unit', 'material']

class PurchaseRequestListSerializer(serializers.ModelSerializer):
    decorator_name = serializers.SerializerMethodField()
    client_name = serializers.SerializerMethodField()
    items = ItemSerializer(many=True)

    def get_client_name(self,obj):
        if not obj.client_name:
            return " "
        return obj.client_name

    def get_decorator_name(self,obj):
        return f"{obj.decorator.user.first_name} {obj.decorator.user.first_name}"

    class Meta:
        model = PurchaseRequest
        fields =['pk','decorator_name', 'items', 'price', 'billing_address', 'shipping_address', 'created_at', 'is_approved', 'is_rejected', 'client_name']


##################################################### WALLRUS ADMIN SERIALIZERS ###################################################
class DesignListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Design
        fields = ['id', 'name', 'is_customizable']

class ColorwayListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Colorway
        fields = ['id', 'name', 'image_url']


class DesignDetailSerializer(serializers.ModelSerializer):
    tags = UploadDesignTagSerializer(many=True)
    applications = ApplistSerializer(many=True)
    colorway_set = ColowaySerializer(many=True)

    class Meta:
        model = Design
        fields = ['id', 'name', 'tags', 'is_customizable',
                  'applications', 'colorway_set']


class PostListSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self,obj):
        try:
            return obj.image.url
        except:
            return ""
    class Meta:
        model = Post
        fields = ['created_at', 'title', 'category', 'slug', 'image']


class PostDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['title', 'content']


class NewArtistsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'first_name', 'last_name', 'email', 'is_active']


class NewPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['title', 'category', 'content']


class OrderListSerializer(serializers.ModelSerializer):
    order_cost = serializers.SerializerMethodField()

    def get_order_cost(self, obj):
        order_cost = 0
        for item in obj.items.all():
            order_cost += item.product.cost * item.quantity
        return order_cost

    class Meta:
        model = Order
        fields = ['id', 'order_cost']




class OrderDetailSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    def get_items(self, obj):
        items = Item.objects.filter(order=obj)
        return ItemSerializer(items, many=True).data

    def get_status(self, obj):
        status = OrderStatus.objects.filter(order = obj)[0].name
        return status

    class Meta:
        model = Order
        fields = ['id', 'items', 'order_cost', 'status']


class AdminArtistDetailSerializer(serializers.ModelSerializer):
    business_details = BusinessDetailSerializer()

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'username',
                  'business_details', 'address_set']


class UpdateArtistStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['is_active']


class UpdateDesignStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Design
        fields = ['is_approved', 'is_rejected']


class UpdateOrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatus
        fields = ['order', 'name']


class MonthlySalesSerializer(serializers.ModelSerializer):
    sales = serializers.SerializerMethodField()

    def get_sales(self, obj):
        order_cost = 0
        for item in obj.items.all():
            order_cost += item.product.cost * item.quantity
        return order_cost

    class Meta:
        model = Order
        fields = ['created_at', 'sales']


class MonthlyDecoratorCountSerializer(serializers.ModelSerializer):
    decorators_count = serializers.SerializerMethodField()

    def get_decorators_count(self, obj):
        return Interior_Decorator.objects.filter(user__date_joined__date=obj[0]).values('user__date_joined__date').annotate(
            noOfDecorators=Count('user__date_joined')).order_by()

    class Meta:
        model = Interior_Decorator
        fields = ['decorators_count']


class MonthlyArtistCountSerializer(serializers.ModelSerializer):
    artists_count = serializers.SerializerMethodField()

    def get_artists_count(self, obj):
        return Artist.objects.filter(user__date_joined__date=obj[0]).values('user__date_joined__date').annotate(
            noOfartists=Count('user__date_joined')).order_by()

    class Meta:
        model = Artist
        fields = ['artists_count']


class MonthlyBarChartSerializer(serializers.ModelSerializer):
    count = serializers.SerializerMethodField()

    def get_count(self, obj):
        artists = Artist.objects.filter(user__date_joined__date=obj[0]).values('user__date_joined__date').annotate(
            noOfartists=Count('user__date_joined')).order_by()
        decorators = Interior_Decorator.objects.filter(user__date_joined__date=obj[0]).values('user__date_joined__date').annotate(
            noOfDecorators=Count('user__date_joined')).order_by()
        return artists, decorators

    class Meta:
        model = Artist
        fields = ['count']

class NewDecoratorsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        # fields = '__all__'
        fields = ['id', 'first_name', 'last_name', 'email', 'phone', 'is_active']

class RequestMeasurementVerifySerializer(serializers.ModelSerializer):
    class Meta:
        model = MeasurementRequest
        fields = ["is_approved"]

class DesignTagListSerializer(serializers.ModelSerializer):
    class Meta:
        model = DesignTag
        fields = ["id", "name", "label", "is_approved"]

class DesignTagVerifySerializer(serializers.ModelSerializer):
    class Meta:
        model = DesignTag
        fields = ["is_approved"]

############################################# DECORATOR SERIALIZERS ###################################################################


class DecoratorSnippetSerializer(serializers.ModelSerializer):
    level = serializers.SerializerMethodField()
    is_firm_user = serializers.SerializerMethodField()
    reward_points = serializers.SerializerMethodField()
    comission_percent = serializers.SerializerMethodField()
    revenue = serializers.SerializerMethodField()

    def get_comission_percent(self, obj):

        return obj.interior_decorator.get_commision_percent()

    def get_level(self, obj):
        try:
            obj.interior_decorator.level.get_name_display()
        except:
            try:
                entry_level = CommissionGroup.objects.filter(name = 1)[0]
            except:
                entry_level = CommissionGroup(name = 1)
                entry_level.save()
            obj.interior_decorator(level = self.entry_level)
            obj.save()
        return obj.interior_decorator.level.get_name_display()

    def get_is_firm_user(self,obj):
        try:
            c = obj.members.all().count()
            if c > 0:
                return True
            else:
                return False
        except:
            return False

    def get_reward_points(self,obj):
        return obj.interior_decorator.reward_points

    def get_revenue(self, obj):
        try:
            now = timezone.now()
            start_date = now -timedelta(days=30)
            dec_order = Order.objects.filter(user = obj, created_at__gte=start_date)
            decorator_rev = dec_order.aggregate(Sum('order_cost'))['order_cost__sum']
            if decorator_rev in None:
                return 0
            return decorator_rev
        except:
            return 0

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'level', 'profile_picture', 'is_firm_user','reward_points', 'email', 'comission_percent','revenue']


class FavouriteSerializer(serializers.ModelSerializer):
    artist = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    artist_image = serializers.SerializerMethodField(allow_null=True)

    def get_artist(self, obj):
        return obj.design.get_artist_name()

    def get_image(self, obj):
        return obj.get_display_image()

    def get_artist_image(self, obj):
        return obj.get_artist_image()

    class Meta:
        model = Product
        fields = ['sku', 'artist', 'image', 'artist_image', 'slug']


class ProductSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    artist_name = serializers.SerializerMethodField()
    artist_picture = serializers.SerializerMethodField()
    is_favourite = serializers.SerializerMethodField(allow_null=True)

    def get_image(self, obj):
        return obj.get_display_image()

    def get_artist_name(self, obj):
        return obj.get_artist_name()

    def get_artist_picture(self, obj):
        return obj.get_artist_image()

    def get_is_favourite(self, obj):
        fav = Product.objects.filter(sku = obj.sku, favourited_by__email=self.context['request'].user, favourited_by__is_active=True).exists()
        return fav

    class Meta:
        model = Product
        fields = ['sku','artist_name', 'artist_picture', 'is_favourite', 'image', 'slug']


class CollectionSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True)
    number_of_designs = serializers.SerializerMethodField()
    number_of_artists = serializers.SerializerMethodField()
    tag = serializers.SerializerMethodField()

    def get_number_of_designs(self, obj):
        designs = []
        for product in obj.products.all():
            if product.design not in designs:
                designs.append(product.design)
        return len(designs)

    def get_number_of_artists(self, obj):
        artists = []
        for product in obj.products.all():
            if product.design.artist not in artists:
                artists.append(product.design.artist)
        return len(artists)
    
    def get_tag(self, obj):
        return obj.get_tag()

    class Meta:
        model = Collection
        fields = ['pk', 'name', 'products',
                  'number_of_designs', 'number_of_artists', 'description', 'tag', 'updated_on']


class OrderItemSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    cost = serializers.SerializerMethodField()
    artist = serializers.SerializerMethodField()
    material = serializers.SerializerMethodField()

    def get_image(self, obj):
        return obj.product.get_display_image()

    def get_name(self, obj):
        return f'{obj.product.design.name}.{obj.product.colorway.name}.{obj.product.application}'

    def get_cost(self, obj):
        return obj.price

    def get_artist(self, obj):
        return obj.product.design.artist.first_name + ' ' + obj.product.design.artist.last_name

    def get_material(self, obj):
        try:
            res = obj.material.name
        except:
            res = "Material"
        return res

    class Meta:
        model = Item
        fields = ['image', 'name', 'cost',
                  'quantity', 'width', 'height', 'artist', 'material']


class MyOrderSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()
    order_status = serializers.SerializerMethodField()

    def get_items(self,obj):
        items = Item.objects.filter(order=obj)
        return OrderItemSerializer(items, many=True).data

    def get_order_status(self, obj):
        try:
            res = obj.order_status.all().order_by('-timestamp').first().name
        except:
            res = "pending"
        return res

    class Meta:
        model = Order
        fields = ['id', 'items', 'order_status']

class CustomizeDesignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customization
        exclude = ['id']

class RequestMeasurementSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeasurementRequest
        fields = "__all__"
        # exclude = ['id']

class UploadOwnDesignSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadOwnDesign
        exclude = ['id']

class ArtistPublicSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    profile_picture = serializers.SerializerMethodField()
    number_of_designs = serializers.SerializerMethodField()
    number_of_followers = serializers.SerializerMethodField()
    following = serializers.SerializerMethodField()
    
    def get_full_name(self, obj):
        return obj.user.first_name + ' ' + obj.user.last_name

    def get_profile_picture(self, obj):
        if obj.user.profile_picture:
            return obj.user.profile_picture.url
    
    def get_number_of_designs(self, obj):
        return obj.get_total_designs()

    def get_number_of_followers(self, obj):
        return obj.followers.count()

    def get_following(self, obj):
        temp = Artist.objects.filter(
            followers__user__email=self.context['request'].user, pk=obj.user.id).exists()
        return temp

    class Meta:
        model = Artist
        fields = ['full_name', 'profile_picture', 'number_of_designs', 'number_of_followers', 'following']


class ResetPasswordEmailRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=2)

    class Meta:
        fields = ['email']

    def validate(self, attrs):
        email = attrs['data'].get('email', '')
        return super().validate(attrs)


class SetNewPassswordSerializer(serializers.Serializer):
    password = serializers.CharField(min_length=6, max_length=68, write_only=True)
    token = serializers.CharField(min_length=1, write_only=True)
    uidb64 = serializers.CharField(min_length=1, write_only=True)

    class Meta:
        fields = ['password', 'token', 'uidb64']

    def validate(self, attrs):
        try:
            password = attrs.get('password')
            token=attrs.get('token')
            uidb64 = attrs.get('uidb64')

            id = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                raise APIException.AuthenticationFailed('The reset link is invalid', 401)

            user.set_password(password)
            user.save()

            return user
        except Exception as e:
            raise APIException.AuthenticationFailed('The reset link is invalid', 401)

        return super().validate(attrs)

class CoinTransactionListSerializer(serializers.ModelSerializer):

    created_at = serializers.SerializerMethodField()

    def get_created_at(self, obj):
        return obj.created_at.strftime("%m %b, %Y at %H:%M")

    class Meta:
        model = CoinTransaction
        fields = "__all__"

class LevelListSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    def get_name(self, obj):
        return obj.get_name_display()

    class Meta:
        model = CommissionGroup
        fields = ['name', 'min_revenue']