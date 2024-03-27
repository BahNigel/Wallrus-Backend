from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from users.models import CustomUser
from product.models import Product, Application, Tag
from designs.models import Design
from ..serializers import *
from api.custom_pagination import CustomPageNumberPagination
from notifications.models import UserNotifications


class FilterList(APIView):
    '''
    Tags list by label for upload design form
    '''

    def get_tag_label_by_products(self, application_slug):
        return Product.objects.filter(
            application__slug=application_slug).values('design__tags__label').distinct()

    def get(self, request, application_slug):
        list = self.get_tag_label_by_products(application_slug)

        tags = DesignTag.objects.filter(label__in=list).values('label').distinct()
        serializer = FilterSerializer(instance=tags, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class ApplicationProductList(APIView):
    permission_classes = [IsAuthenticated]

    def get_objects(self, application_slug,sort):
        if sort is None or sort =="new":
            return Product.objects.filter(is_active=True, application__slug=application_slug, application__is_active=True).order_by('-created_at')
        else:
            if sort == 'ratings':
                products = Product.objects.filter(is_active=True, application__slug=application_slug, application__is_active=True)
                return sorted(products, key = lambda p: float(p.get_average_rating()), reverse=True)
            elif sort =="selling" or sort =="recommended":
                products = Product.objects.filter(is_active=True, application__slug=application_slug, application__is_active=True)
                return sorted(products, key = lambda p: p.get_total_sale(), reverse=True)
            else:
                return Product.objects.filter(is_active=True, application__slug=application_slug, application__is_active=True).order_by('-created_at')

    def get(self, request, application_slug):
        sort = request.GET.get('sort-by',None)
        object = self.get_objects(application_slug,sort)
        context = {'request': request}
        paginator = CustomPageNumberPagination()
        result_page = paginator.paginate_queryset(object,request)
        serializer = ProductListSerializer(instance=result_page, many=True, context=context)
        return paginator.get_paginated_response(serializer.data)
        # return Response(data=serializer.data, status=status.HTTP_200_OK)

class MaterialListView(APIView):

    def get(self,request,application_slug):
        materials = Material.objects.filter(application__slug = application_slug)
        serializer = MaterialSerializer(materials, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

class ProductDetail(APIView):
    permission_classes = [IsAuthenticated]

    def get_product_object(self, product_slug):
        return get_object_or_404(Product, is_active=True, slug=product_slug)

    def get(self, request, product_slug):
        object = self.get_product_object(product_slug)
        if request.user.type == 2:
            print("view increased")
            object.views = object.views + 1
            object.save()
            nt_ins2 = UserNotifications(user=object.design.artist, notification_type='design_view', text=f"{request.user.first_name} {request.user.last_name} Viewd {object.design.name}")
            nt_ins2.save()
        context = {'request': request}
        serializer = ProductDetailSerializer(instance=object, context=context)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class OtherColorways(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, product_slug):
        designs = Product.objects.filter(
            is_active=True, slug=product_slug).values_list('design__name', flat=True)
        return Product.objects.filter(design__name=designs.first(), is_active=True).exclude(slug=product_slug)

    def get(self, request, product_slug):
        object = self.get_object(product_slug)
        paginator = CustomPageNumberPagination()
        result_page = paginator.paginate_queryset(object,request)
        context = {'request': request}
        serializer = ProductListSerializer(instance=result_page, many=True, context=context)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class OtherApplications(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, product_slug):
        applications = Product.objects.filter(
            is_active=True, slug=product_slug).values_list('application__name', flat=True)
        return Product.objects.filter(is_active=True).exclude(application__name=applications.first())

    def get(self, request, product_slug):
        object = self.get_object(product_slug)
        paginator = CustomPageNumberPagination()
        result_page = paginator.paginate_queryset(object,request)
        context = {'request': request}
        serializer = ProductListSerializer(instance=result_page, many=True, context=context)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class SimilarDesigns(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, product_slug):
        applications = Product.objects.filter(
            is_active=True, slug=product_slug).values_list('application__name', flat=True)
        return Product.objects.filter(application__name=applications.first(), is_active=True).exclude(slug=product_slug)

    def get(self, request, product_slug):
        object = self.get_object(product_slug)
        paginator = CustomPageNumberPagination()
        result_page = paginator.paginate_queryset(object,request)
        context = {'request': request}
        serializer = ProductListSerializer(instance=result_page, many=True, context=context)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

class DesignerListView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, application_slug):
        design = Product.objects.filter(
            is_active=True, application__slug=application_slug).values_list('design__name', flat=True).distinct()
        return Design.objects.filter(name__in=design,is_approved=True).distinct()

    def get(self, request, application_slug):
        object = self.get_object(application_slug)
        paginator = CustomPageNumberPagination()
        result_page = paginator.paginate_queryset(object,request)
        serializer = DesignListSerializer(instance=result_page, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

class FilterTagList(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, tags, application_slug):
        print(type(tags))
        return Product.objects.filter(design__tags__name__in=tags, application__slug=application_slug).order_by('-created_at').distinct()

    def post(self, request):
        tags = request.data['tags']
        application_slug = request.data['application_slug']
        print(tags)
        object = self.get_object(tags, application_slug)
        context = {'request': request}
        paginator = CustomPageNumberPagination()
        result_page = paginator.paginate_queryset(object,request)
        serializer = ProductListSerializer(instance=result_page, many=True, context=context)
        return paginator.get_paginated_response(serializer.data)
        # return Response(data=serializer.data, status=status.HTTP_200_OK)

class LatestDesignList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        object = Product.objects.order_by('-created_at')[:10]
        context = {'request': request}
        paginator = CustomPageNumberPagination()
        result_page = paginator.paginate_queryset(object,request)
        serializer = ProductListSerializer(instance=result_page, many=True, context=context)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

class FollowedArtistProduct(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        decorator = Interior_Decorator.objects.get(user=request.user)
        object = []
        followed_artists = Artist.objects.filter(followers=decorator)
        for artist in followed_artists:
            products =   Product.objects.filter(design__artist = artist.user)
            for product in products:
                object.append(product)
        context = {'request': request}
        serializer = ProductListSerializer(instance=object, many=True, context=context)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

class DesignListView(APIView):
    permission_classes = [AllowAny]
    def get(self,request):
        object = Product.objects.all()
        paginator = CustomPageNumberPagination()
        result_page = paginator.paginate_queryset(object,request)
        serializer = DesignSerializer(instance=result_page, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

class ProductReviewView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        sku = request.data['sku']
        print(sku)
        object = Reviews.objects.filter(product__sku = sku)
        paginator = CustomPageNumberPagination()
        result_page = paginator.paginate_queryset(object,request)
        serializer = DesignSerializer(instance=result_page, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        sku = request.POST.get('sku')
        product = Product.objects.get(sku = sku)
        user = request.user
        rating = request.POST.get('rating')
        review = request.POST.get('review')
        print(sku,user,rating, review)
        ins = Reviews(product = product, reviewer = user, rating = rating, review = review)
        ins.save()
        return Response(data='Review Added', status=status.HTTP_201_CREATED)