from rest_framework import serializers
from orders.models import ClientCart, ClientDetails, Item, Cart
from api.serializers import ProductDetailSerializer, DecoratorSnippetSerializer,ProductImagesSerializer, ReviewsSerializer, AddressSerializer
from product.models import Coupon, Product


class ClientProductDetailSerializer(serializers.ModelSerializer):
    ratings = serializers.SerializerMethodField()
    number_of_ratings = serializers.SerializerMethodField()
    productimages_set = ProductImagesSerializer(many=True)
    application = serializers.SerializerMethodField()
    colorway = serializers.SerializerMethodField()
    artist = serializers.SerializerMethodField()
    artist_unique_id = serializers.SerializerMethodField()
    reviews_set = ReviewsSerializer(many=True)
    design_name = serializers.SerializerMethodField()

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

    def get_colorway(self, obj):
        return obj.colorway.name

    def get_design_name(self, obj):
        return obj.design.name


    class Meta:
        model = Product
        fields = ['sku', 'application', 'colorway', 'design_name', 'productimages_set',
                  'artist', 'artist_unique_id', 'ratings', 'number_of_ratings', 'reviews_set',]

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'

class ItemListSerializer(serializers.ModelSerializer):
    product = ProductDetailSerializer()
    material = serializers.SerializerMethodField()

    def get_material(self, obj):
        try:
            res = obj.material.name
        except:
            res = ""
        return res
        
    class Meta:
        model = Item
        fields = ['id','product', 'quantity', 'width', 'height', 'unit', 'material', 'price']

class CartSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()

    def get_items(self,obj):
        items = Item.objects.filter(cart=obj)
        return ItemListSerializer(items, many=True, context = {'request':self.context['request']}).data
        
    class Meta:
        model = Cart
        # fields = "__all__"
        fields = ['id', 'user', 'is_shared', 'created_at', 'items']

class ClientDetailsSerializer(serializers.ModelSerializer):
    decorator = DecoratorSnippetSerializer()
    class Meta:
        model = ClientDetails
        fields = '__all__'

class ClientCartSerializer(serializers.ModelSerializer):
    client = ClientDetailsSerializer()
    items = ItemListSerializer(many=True)
    class Meta:
        model = ClientCart
        fields = '__all__'

class ClientViewItemListSerializer(serializers.ModelSerializer):
    product = ClientProductDetailSerializer()
    material = serializers.SerializerMethodField()

    def get_material(self, obj):
        try:
            mat = obj.material.name
        except:
            mat = ""
        
        return mat
    class Meta:
        model = Item
        fields = ['id','product', 'quantity', 'width', 'height', 'unit', 'material', 'price']

class ClientViewCartSerializer(serializers.ModelSerializer):
    client = ClientDetailsSerializer()
    items = ClientViewItemListSerializer(many=True)
    class Meta:
        model = ClientCart
        fields = '__all__'

class CouponDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = '__all__'
