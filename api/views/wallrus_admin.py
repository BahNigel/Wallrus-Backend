from datetime import date
import calendar
from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from api.custom_pagination import CustomPageNumberPagination
from designs.models import Colorway, Design, DesignTag
from posts.models import Post
from users.models import CustomUser, Interior_Decorator, Artist
from orders.models import Order, MeasurementRequest
from ..serializers import (
    ColorwayListSerializer,
    DesignListSerializer, 
    DesignDetailSerializer,
    PostListSerializer,
    PostDetailSerializer, 
    NewArtistsSerializer, 
    NewPostSerializer, 
    OrderListSerializer, 
    OrderDetailSerializer, 
    AdminArtistDetailSerializer, 
    UpdateArtistStatusSerializer, 
    UpdateDesignStatusSerializer, 
    UpdateOrderStatusSerializer, 
    MonthlySalesSerializer, 
    MonthlyDecoratorCountSerializer, 
    MonthlyArtistCountSerializer, 
    MonthlyBarChartSerializer,
    NewDecoratorsSerializer,
    RequestMeasurementVerifySerializer,
    RequestMeasurementSerializer,
    DesignTagListSerializer,
    DesignTagVerifySerializer,
)


class DesignList(APIView):
    permission_classes = [AllowAny]

    def get_design_list(self):
        return Design.objects.all().order_by('-id')

    def get(self, request):
        objects = self.get_design_list()
        keyword = request.GET.get('keyword', None)
        if keyword and keyword != '' and keyword != ' ':
            query_design = Q()
            words = keyword.split(' ')
            for w in words:
                query_design |= Q(pk__icontains=w)
                query_design |= Q(name__icontains=w)
                query_design |= Q(tags__name__icontains=w)
                query_design |= Q(artist__first_name__icontains=w)
                query_design |= Q(artist__last_name__icontains=w)
                query_design |= Q(artist__email__icontains=w)
            objects = objects.filter(query_design).distinct()
        paginator = CustomPageNumberPagination()
        result_page = paginator.paginate_queryset(objects,request)
        serializer = DesignListSerializer(instance=result_page, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

class ColorwayList(APIView):
    permission_classes = [AllowAny]

    def get(self,request):
        objects = Colorway.objects.all()
        keyword = request.GET.get('keyword', None)
        if keyword and keyword != '' and keyword != ' ':
            query_colorway = Q()
            words = keyword.split(' ')
            for w in words:
                query_colorway |= Q(pk__icontains=w)
                query_colorway |= Q(name__icontains=w)
                query_colorway |= Q(color_tags__name__icontains=w)
            objects = objects.filter(query_colorway).distinct()
        paginator = CustomPageNumberPagination()
        result_page = paginator.paginate_queryset(objects,request)
        serializer = ColorwayListSerializer(instance=result_page, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class DesignDetail(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_design_object(self, design_id):
        return get_object_or_404(Design, id=design_id)

    def get(self, request, design_id):
        object = self.get_design_object(design_id)
        serializer = DesignDetailSerializer(instance=object)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class PostList(APIView):
    permission_classes = [IsAdminUser, IsAuthenticated]

    def get_post_list(self):
        return Post.objects.all().order_by('-id')

    def get(self, request):
        objects = self.get_post_list()
        serializer = PostListSerializer(instance=objects, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class PostDetail(APIView):
    permission_classes = [IsAdminUser, IsAuthenticated]

    def get_post_object(self, post_slug):
        return get_object_or_404(Post, slug=post_slug)

    def get(self, request, post_slug):
        object = self.get_post_object(post_slug)
        serializer = PostDetailSerializer(instance=object)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class CreatePost(APIView):
    permission_classes = [IsAdminUser, IsAuthenticated]

    def post(self, request):
        serializer = NewPostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data={'message': 'The post has been created'}, status=status.HTTP_200_OK)
        return Response(data={'error': 'Bad Request'}, status=status.HTTP_400_BAD_REQUEST)


class NewArtists(APIView):
    permission_classes = [IsAdminUser, IsAuthenticated]

    def get_artist_objects(self, from_date, to_date):
        artists = CustomUser.objects.filter(type=1, is_active=True)

        return [artist for artist in artists if (artist.date_joined.date() >= from_date and artist.date_joined.date() <= to_date)]

    def get(self, request):
        curr_date = date.today()
        curr_month = curr_date.month
        curr_year = curr_date.year

        start_date = date(curr_year, curr_month, 1)

        objects = self.get_artist_objects(start_date, curr_date)
        serializer = NewArtistsSerializer(instance=objects, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class OrderList(APIView):
    permission_classes = [IsAdminUser, IsAuthenticated]

    def get_order_objects(self):
        return Order.objects.all().order_by('-id')

    def get(self, request):
        objects = self.get_order_objects()
        serializer = OrderListSerializer(instance=objects, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class OrderDetail(APIView):
    permission_classes = [IsAdminUser, IsAuthenticated]

    def get_order_object(self, order_id):
        return get_object_or_404(Order, id=order_id)

    def get(self, request, order_id):
        object = self.get_order_object(order_id)
        serializer = OrderDetailSerializer(instance=object)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class AdminArtistDetail(APIView):
    permission_classes = [IsAdminUser, IsAuthenticated]

    def get_user_object(self, artist_id):
        return get_object_or_404(CustomUser, id=artist_id, type=1)

    def get(self, request, artist_id):
        object = self.get_user_object(artist_id)
        print(object)
        serializer = AdminArtistDetailSerializer(instance=object)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class ApproveArtist(APIView):
    permission_classes = [IsAdminUser, IsAuthenticated]

    def get_user_object(self, artist_id):
        return get_object_or_404(CustomUser, id=artist_id, type=1)

    def patch(self, request, artist_id):
        object = self.get_user_object(artist_id)
        artist_status = request.GET['status']
        if artist_status == 'approve':
            data = {
                'is_active': True
            }
        elif artist_status == 'reject':
            data = {
                'is_active': False
            }
        serializer = UpdateArtistStatusSerializer(instance=object, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(data={'message': 'Status Updated'}, status=status.HTTP_200_OK)
        else:
            print(serializer.errors)
            return Response(data={'error': 'Bad Request'}, status=status.HTTP_400_BAD_REQUEST)


class ApproveDesign(APIView):
    permission_classes = [IsAdminUser, IsAuthenticated]

    def get_design_object(self, design_id):
        return get_object_or_404(Design, id=design_id)

    def patch(self, request, design_id):
        object = self.get_design_object(design_id)
        design_status = request.GET['status']
        if design_status == 'approve':
            data = {
                'is_approved': True,
                'is_rejected': False
            }
        elif design_status == 'reject':
            data = {
                'is_approved': False,
                'is_rejected': True
            }
        serializer = UpdateDesignStatusSerializer(instance=object, data=data)
        print(serializer)
        if serializer.is_valid():
            serializer.save()
            return Response(data={'message': 'Status Updated'}, status=status.HTTP_200_OK)
        else:
            print(serializer.errors)
            return Response(data={'error': 'Bad Request'}, status=status.HTTP_400_BAD_REQUEST)


class ApproveOrder(APIView):
    permission_classes = [IsAdminUser, IsAuthenticated]

    def post(self, request, order_id):
        order_status = request.GET['status']
        if order_status == 'approve':
            data = {
                'order': order_id,
                'name': 'confirmed'
            }
        elif order_status == 'reject':
            data = {
                'order': order_id,
                'name': 'rejected'
            }
        serializer = UpdateOrderStatusSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(data={'message': 'Status Updated'}, status=status.HTTP_200_OK)
        else:
            print(serializer.errors)
            return Response(data={'error': 'Bad Request'}, status=status.HTTP_400_BAD_REQUEST)


class MonthlySales(APIView):
    permission_classes = [IsAdminUser, IsAuthenticated]

    def get_order_objects(self, from_date, to_date):
        orders = Order.objects.filter(
            created_at__gte=from_date) & Order.objects.filter(created_at__lte=to_date)
        return orders

    def get(self, request):
        cur_date = date.today()
        start_date = date(cur_date.year, cur_date.month, 1)

        objects = self.get_order_objects(start_date, cur_date)
        serializer = MonthlySalesSerializer(instance=objects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MonthlyDecoratorsCount(APIView):
    permission_classes = [IsAdminUser, IsAuthenticated]

    def get_decorator_objects(self, from_date, to_date):
        decorators = Interior_Decorator.objects.filter(user__is_active=True)
        decorators = decorators.filter(user__date_joined__date__gte=from_date) & decorators.filter(
            user__date_joined__date__lte=to_date)

        decorators = decorators.values_list(
            'user__date_joined__date').distinct()
        return decorators

    def get(self, request):
        cur_date = date.today()
        last_day_of_month = calendar.monthrange(
            cur_date.year, cur_date.month)[1]
        start_date = date(cur_date.year, cur_date.month, 1)
        end_date = date(cur_date.year, cur_date.month, last_day_of_month)

        objects = self.get_decorator_objects(start_date, end_date)
        serializer = MonthlyDecoratorCountSerializer(
            instance=objects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MonthlyArtistsCount(APIView):
    permission_classes = [IsAdminUser, IsAuthenticated]

    def get_artist_objects(self, from_date, to_date):
        artists = Artist.objects.filter(user__is_active=True)
        artists = artists.filter(user__date_joined__date__gte=from_date) & artists.filter(
            user__date_joined__date__lte=to_date)

        artists = artists.values_list(
            'user__date_joined__date').distinct()
        return artists

    def get(self, request):
        cur_date = date.today()
        last_day_of_month = calendar.monthrange(
            cur_date.year, cur_date.month)[1]
        start_date = date(cur_date.year, cur_date.month, 1)
        end_date = date(cur_date.year, cur_date.month, last_day_of_month)

        objects = self.get_artist_objects(start_date, end_date)
        serializer = MonthlyArtistCountSerializer(
            instance=objects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MonthlyBarChart(APIView):
    permission_classes = [IsAdminUser, IsAuthenticated]

    def get_artist_objects(self, from_date, to_date):
        artists = Artist.objects.filter(user__is_active=True)
        artists = artists.filter(user__date_joined__date__gte=from_date) & artists.filter(
            user__date_joined__date__lte=to_date)

        artists = artists.values_list(
            'user__date_joined__date').distinct()
        return artists

    def get(self, request):
        cur_date = date.today()
        last_day_of_month = calendar.monthrange(
            cur_date.year, cur_date.month)[1]
        start_date = date(cur_date.year, cur_date.month, 1)
        end_date = date(cur_date.year, cur_date.month, last_day_of_month)

        objects = self.get_artist_objects(start_date, end_date)
        serializer = MonthlyBarChartSerializer(
            instance=objects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PieChart(APIView):
    permission_classes = [IsAdminUser, IsAuthenticated]

    def get_total_artists(self):
        return Artist.objects.all().count()

    def get_total_decorators(self):
        return Interior_Decorator.objects.all().count()

    def get(self, request):
        data = {
            'totalArtists': self.get_total_artists(),
            'totalDecorators': self.get_total_decorators()
        }
        return Response(data, status=status.HTTP_200_OK)

class NewDecoratorsView(APIView):
    permission_classes = [IsAdminUser, IsAuthenticated]

    def get_user_object(self, decorator_id):
        return get_object_or_404(CustomUser, id=decorator_id, type=2)

    def get(self, request, decorator_id=None):
        if decorator_id is not None:
            object = self.get_user_object(decorator_id)
            serializer = NewDecoratorsSerializer(instance=object)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
            
        objects = CustomUser.objects.filter(type=2, is_active=False)
        serializer = NewDecoratorsSerializer(instance=objects, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, decorator_id):
        object = self.get_user_object(decorator_id)
        decorator_status = request.GET['status']
        if decorator_status == 'approve':
            data = {
                'is_active': True
            }
        elif decorator_status == 'reject':
            data = {
                'is_active': False
            }
        serializer = UpdateArtistStatusSerializer(instance=object, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(data={'message': 'Status Updated'}, status=status.HTTP_200_OK)
        else:
            print(serializer.errors)
            return Response(data={'error': 'Bad Request'}, status=status.HTTP_400_BAD_REQUEST)

class RequestMeasurementVerifyView(APIView):
    permission_classes = [IsAdminUser, IsAuthenticated]

    def get_request_measument_object(self, request_measurement_id):
        return get_object_or_404(MeasurementRequest, id=request_measurement_id)

    def get(self, request, request_measurement_id=None):
        if request_measurement_id is not None:
            object = self.get_request_measument_object(request_measurement_id)
            serializer = RequestMeasurementSerializer(instance=object)
            return Response(data=serializer.data, status=status.HTTP_200_OK)

        objects = MeasurementRequest.objects.filter(is_approved=False).order_by('id')
        serializer = RequestMeasurementSerializer(instance=objects, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, request_measurement_id):
        object = self.get_request_measument_object(request_measurement_id)
        request_measurement_status = request.GET['status']
        if request_measurement_status == 'approve':
            data = {
                'is_approved': True
            }
        elif request_measurement_status == 'reject':
            data = {
                'is_approved': False
            }
        serializer = RequestMeasurementVerifySerializer(instance=object, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(data={'message': 'Status Updated'}, status=status.HTTP_200_OK)
        else:
            print(serializer.errors)
            return Response(data={'error': 'Bad Request'}, status=status.HTTP_400_BAD_REQUEST)

class DesignTagVerifyView(APIView):
    permission_classes = [IsAdminUser, IsAuthenticated]

    def get_design_tag_object(self, id):
        return get_object_or_404(DesignTag, id=id)

    def get(self, request, design_tag_id=None):
        if design_tag_id is not None:
            object = self.get_design_tag_object(design_tag_id)
            serializer = DesignTagListSerializer(instance=object)
            return Response(data=serializer.data, status=status.HTTP_200_OK)

        objects = DesignTag.objects.filter(is_approved=False).order_by('id')
        serializer = DesignTagListSerializer(instance=objects, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, design_tag_id):
        object = self.get_design_tag_object(design_tag_id)
        request_status = request.GET['status']
        if request_status == 'approve':
            data = {
                'is_approved': True
            }
        elif request_status == 'reject':
            data = {
                'is_approved': False
            }
        serializer = DesignTagVerifySerializer(instance=object, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(data={'message': 'Status Updated'}, status=status.HTTP_200_OK)
        else:
            print(serializer.errors)
            return Response(data={'error': 'Bad Request'}, status=status.HTTP_400_BAD_REQUEST)