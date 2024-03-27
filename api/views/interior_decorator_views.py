from datetime import date
import calendar
from unicodedata import category
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from users.models import CustomUser, Artist
from product.models import Product, Collection, CollectionTag, Application
from orders.models import Order
from posts.models import Post
from user_details.models import CoinTransaction
from notifications.models import UserNotifications
from levels.models import CommissionGroup

from ..serializers import ArtistPublicSerializer, CoinTransactionListSerializer, CollectionSerializer, DecoratorSnippetSerializer, FavouriteSerializer, \
    MyOrderSerializer, CustomizeDesignSerializer, RequestMeasurementSerializer, UploadOwnDesignSerializer, PostListSerializer, \
        ArtistPublicSerializer, LevelListSerializer
from api.custom_pagination import CustomPageNumberPagination
from api.utils import send_admin_mail


class DecoratorSnippet(APIView):
    permission_classes = [IsAuthenticated]

    def get_decorator_object(self, decorator_email):
        return get_object_or_404(CustomUser, type=2, email=decorator_email, is_active=True)

    def get(self, request):
        object = self.get_decorator_object(request.user)
        serializer = DecoratorSnippetSerializer(instance=object)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DecoratorFavourites(APIView):
    permission_classes = [IsAuthenticated]

    def get_product_objects(self, decorator_email):
        return Product.objects.filter(favourited_by__email=decorator_email, favourited_by__is_active=True).order_by('-created_at')

    def get(self, request):
        objects = self.get_product_objects(request.user)
        paginator = CustomPageNumberPagination()
        result_page = paginator.paginate_queryset(objects,request)
        serializer = FavouriteSerializer(instance=result_page, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        product_id = request.data["product_id"]
        product = Product.objects.get(pk=product_id)
        custom_user = CustomUser.objects.get(email=request.user)
        product.favourited_by.add(custom_user)
        return Response({'details': "The requesting user successfully favourited the product."}, status=status.HTTP_201_CREATED)
        
class AddToFavourites(APIView):
    permission_classes = [IsAuthenticated]
    def get_product_objects(self, decorator_email,sku):
        return Product.objects.filter(sku=sku, favourited_by__email=decorator_email, favourited_by__is_active=True)

    def get_product_object(self, sku):
        return Product.objects.get(sku=sku)

    def get(self,request,sku):
        product = self.get_product_object(sku)
        exists = self.get_product_objects(request.user,sku)
        if exists.count() == 0 :
            product.favourited_by.add(request.user)
            artist = product.design.artist
            nt_ins = UserNotifications(user=artist,creator=request.user, notification_type='design_favorite', text=f"{request.user.first_name} {request.user.last_name} favourited your product named {product.design.name}")
            nt_ins.save()
            return Response({'msg':'Product added to Favourites'}, status=status.HTTP_200_OK)
        else:
            return Response({'msg':'Product already added to Favourites earlier'}, status=status.HTTP_208_ALREADY_REPORTED)
        
class RemoveFromFavourites(APIView):
    permission_classes = [IsAuthenticated]

    def get_product_object(self, sku, decorator_email):
        return Product.objects.get(sku=sku, favourited_by__email=decorator_email)

    def get(self,request,sku):
        try:
            product = self.get_product_object(sku, request.user)
            product.favourited_by.remove(request.user)
            return Response({'msg':'Product Removed From Favourites'}, status=status.HTTP_200_OK)
        except:
            return Response({'msg':"Product doest not exists for this this user's Favourits"}, status=status.HTTP_404_NOT_FOUND)

class DecoratorCollections(APIView):
    permission_classes = [IsAuthenticated]

    def get_collections(self, decorator_email):
        return Collection.objects.filter(user__email=decorator_email, user__is_active=True).order_by('-updated_on')

    def get(self, request, pk=None):
        context = {'request': request}
        if pk is not None:
            object = Collection.objects.get(pk=pk)
            serializer = CollectionSerializer(instance=object, context=context)
            return Response(serializer.data, status=status.HTTP_200_OK)

        objects = self.get_collections(request.user)
        paginator = CustomPageNumberPagination()
        result_page = paginator.paginate_queryset(objects,request)
        serializer = CollectionSerializer(instance=result_page, many=True, context=context)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        try: 
            custom_user = CustomUser.objects.get(email=request.user, is_active=True, type=2)
        except Exception as e:
            return Response({'detail': 'User not found! OR User not active! OR User not a interior decorator!'}, status=status.status.HTTP_401_UNAUTHORIZED)

        collection_name = request.data['collection_name']
        try:
            description = request.data['description']
        except Exception as e:
            description = ''

        collection_obj = Collection(user=custom_user, name=collection_name, description=description)
        collection_obj.save()
        try:
            product_pk = request.data['product_pk']
            product = Product.objects.get(pk=product_pk)
            collection_obj.products.add(product)
        except Exception as e:
            pass
        return Response({'detail': "A new collection has been created for the user and the product has been added to the collection."}, status=status.HTTP_201_CREATED)

    def put(self, request):
        try:
            collection_pk = request.data['collection_pk']
            collection_name = request.data['collection_name']
            collection = Collection.objects.get(pk=collection_pk)
            collection.name = collection_name
            try:
                description = request.data['description']
                collection.description = description
            except Exception as e:
                pass
            collection.save()
            return Response({'detail': "The collection name/description has been updated."}, status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            return Response({'detail': f'{e}'}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        try:
            product_pk = request.data['product_pk']
            collection_pk = request.data['collection_pk']
            product = Product.objects.get(pk=product_pk)
            collection = Collection.objects.get(pk=collection_pk)
            collection.products.add(product)
            try:
                tag_name = request.data['tag_name']
                tag_obj = CollectionTag.objects.create(name=tag_name)
                collection.tag.add(tag_obj)
            except Exception as e:
                pass
            return Response({'detail': "The product/tag has been added to the user's collection."}, status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            return Response({'detail': f'{e}'}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        try: 
            collection_pk = request.data['collection_pk']
            product_pk = request.data['product_pk']
        except Exception:
            product_pk = 0

        if product_pk and collection_pk:
            product = Product.objects.get(pk=product_pk)
            collection = Collection.objects.get(pk=collection_pk)
            collection.products.remove(product)
            return Response({'detail': "The product has been removed from the user's collection."}, status=status.HTTP_200_OK)

        elif collection_pk:
            collection = Collection.objects.get(pk=collection_pk)
            collection.delete()
            return Response({'detail': "The collection has been deleted."}, status=status.HTTP_200_OK)

class MyOrder(APIView):
    permission_classes = [IsAuthenticated]

    def get_order_objects(self, decorator_email):
        return Order.objects.filter(user__email=decorator_email, user__is_active=True).order_by('-id')

    def get(self, request):
        objects = self.get_order_objects(request.user)
        paginator = CustomPageNumberPagination()
        result_page = paginator.paginate_queryset(objects,request)
        serializer = MyOrderSerializer(instance=result_page, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CustomizeDesign(APIView):
    permission_classes = [IsAuthenticated]

    def get_application_id(self, application_slug):
        object = get_object_or_404(Application, slug=application_slug, is_active=True)
        return object.id
    
    def get_product_id(self, product_slug):
        object = get_object_or_404(Product, slug=product_slug)
        return object.sku

    def post(self, request):
        data = {
            'name': request.data['name'],
            'phone_number': request.data['phone_number'],
            'application': self.get_application_id(request.data['application']),
            'product': self.get_product_id(request.data['product']),
            'width': request.data['width'],
            'height': request.data['height'],
            'unit': request.data['unit'],
            'remarks': request.data['remarks'],
            'image1': request.data['image1'],
            'image2': request.data.get('image2', None),
            'image3': request.data.get('image3', None),
            'image4': request.data.get('image4', None),
        }
        serializer = CustomizeDesignSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message':'Data is successfully saved'}, status=status.HTTP_200_OK)
        else:
            print(serializer.errors)
            return Response({'error':'Data is not saved'}, status=status.HTTP_400_BAD_REQUEST)

class RequestMeasurement(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = RequestMeasurementSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            print(serializer.data)
            admin_mail_sub = f"New measurement request by {request.user.email}"
            message = f"A measurement request have been raised, details: https://thewallruscompany.com:8000/admin/orders/measurementrequest/{serializer.data['id']}/change/"
            send_admin_mail(admin_mail_sub,message)
            return Response({'message':'Data is successfully saved'}, status=status.HTTP_200_OK)
        else:
            print(serializer.errors)
            return Response({'error':'Data is not saved'}, status=status.HTTP_400_BAD_REQUEST)


class UploadOwnDesign(APIView):
    permission_classes = [IsAuthenticated]

    def get_application_id(self, application_slug):
        object = get_object_or_404(Application, slug=application_slug, is_active=True)
        return object.id
    
    def get_product_id(self, product_slug):
        object = get_object_or_404(Product, slug=product_slug)
        return object.sku

    def post(self, request):
        data = {
            'name': request.data['name'],
            'phone_number': request.data['phone_number'],
            'application': self.get_application_id(request.data['application']),
            'product': self.get_product_id(request.data['product']),
            'width': request.data['width'],
            'height': request.data['height'],
            'remarks': request.data['remarks'],
            'link': request.data['link'],
            'unit': request.data['unit'],
            'price': request.data['price']
        }
        serializer = UploadOwnDesignSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message':'Data is successfully saved'}, status=status.HTTP_200_OK)
        else:
            print(serializer.errors)
            return Response({'error':'Data is not saved'}, status=status.HTTP_400_BAD_REQUEST)


class ArtistPublic(APIView):
    def get_artist_object(self, unique_id):
        return get_object_or_404(Artist, user__type=1, user__is_active=True)
    
    def get(self, request, unique_id):
        object = self.get_artist_object(unique_id)
        serializer = ArtistPublicSerializer(instance=object)
        return Response(serializer.data, status=status.HTTP_200_OK)

class GetPostList(APIView):
    permission_classes = [IsAuthenticated]

    def get_post_list(self, category):
        return Post.objects.filter(category=category).order_by('-id')

    def get(self, request, category):
        objects = self.get_post_list(category)
        serializer = PostListSerializer(instance=objects, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class CoinTransactionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        list = CoinTransaction.objects.filter(user=request.user)
        paginator = CustomPageNumberPagination()
        result_page = paginator.paginate_queryset(list,request)
        serializer = CoinTransactionListSerializer(instance=result_page,many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LevelListView(APIView):

    def get(self, request):
        levels = CommissionGroup.objects.all()
        serializer = LevelListSerializer(instance=levels, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)