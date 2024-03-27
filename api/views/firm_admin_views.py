from datetime import date
import calendar
from django.shortcuts import get_object_or_404
import random
from requests import request

from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from notifications.models import UserNotifications, InteriorDecoratorNotificationSettings
from levels.models import CommissionGroup

from users.models import Interior_Decorator, CustomUser, Firm
from ..serializers import BusinessDetailSerializer, CardDetailSerializer, FirmUserSerializer, FirmUserListSerializer, FirmOrderSerializer, FirmSalesGraphSerializer, IntDecoratorDetailSerializer, CardDetailSerializer, PurchaseRequestListSerializer,\
    BusinessDetailSerializer, AddUserSerializer, BankDetailSerializer
from orders.models import Order, PurchaseRequest
from api.custom_pagination import CustomPageNumberPagination

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse 
from django.db.models import Q
from ..utils import send_mail


class FirmUserSnippet(APIView):
    permission_classes = [IsAuthenticated]

    def get_user_object(self, firm_email):
        return get_object_or_404(CustomUser, email=firm_email, type=3)

    def get(self, request):
        object = self.get_user_object(request.user)
        serializer = FirmUserSerializer(instance=object)
        return Response(serializer.data, status=status.HTTP_200_OK)


class FirmUsersList(APIView):
    permission_classes = [IsAuthenticated]

    def get_user_objects(self, firm, from_date, to_date):
        decorators = Firm.objects.get(user__email=firm).members.filter(type=2)
        result = []
        if from_date and to_date:
            from_date_array = from_date.split('-')
            end_date_array = to_date.split('-')

            start_date = date(*list(map(int, from_date_array)))
            end_date = date(*list(map(int, end_date_array)))
            for decorator in decorators:
                if decorator.date_joined.date() >= start_date and decorator.date_joined.date() <= end_date:
                    result.append(decorator)
            return result
        return decorators

    def get(self, request):
        from_date = request.GET.get('from_date', None)
        to_date = request.GET.get('to_date', None)
        objects = self.get_user_objects(request.user, from_date, to_date)
        paginator = CustomPageNumberPagination()
        result_page = paginator.paginate_queryset(objects,request)
        serializer = FirmUserListSerializer(instance=result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
        # return Response(serializer.data, status=status.HTTP_200_OK)


class FirmOrders(APIView):
    permission_classes = [IsAuthenticated]

    def get_order_objects(self, firm_email):
        firm = Firm.objects.get(user__email = firm_email)
        members = firm.get_members()
        return Order.objects.filter(user__in = members).order_by('-created_at')

    def get(self, request):
        object = self.get_order_objects(request.user)
        paginator = CustomPageNumberPagination()
        result_page = paginator.paginate_queryset(object,request)
        serializer = FirmOrderSerializer(instance=result_page, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SalesGraph(APIView):
    permission_classes = [IsAuthenticated]

    def get_order_objects(self, firm_email, filter, year_filter):
        firm = Firm.objects.get(user=firm_email)
        members = firm.members.all()
        orders = Order.objects.filter(user__in = members)
        if filter and year_filter:
            months = ['January', 'February', 'March', 'April', 'May', 'June',
                      'July', 'August', 'September', 'October', 'November', 'December']
            month = months.index(filter) + 1
            today = date.today()
            year = int(year_filter)
            start_date = date(year, month, 1)

            if month == today.month and year == today.year:
                end_day = today.day
            else:
                end_day = calendar.monthrange(year, month)[1]
            end_date = date(year, month, end_day)
            print(start_date, end_date)
            orders = orders.filter(created_at__gte=start_date) & orders.filter(
                created_at__lte=end_date)
            date_list = list(range(1,end_day + 1))
            order_count_list = []
            for day in date_list:
                count = orders.filter(created_at__day = day).count()
                order_count_list.append(count)
            date_list_len = len(date_list)
            min_factor = round(date_list_len/10)
            print(min_factor,order_count_list)
            start = 0
            final_val_list = []
            for i in range(int(date_list_len/min_factor)):
                end = start + min_factor
                val_part = order_count_list[start:end]
                avg = sum(val_part)/min_factor
                final_val_list.append(avg)
                start = end
            if date_list_len - (end -1) > 0:
                left = order_count_list[end:date_list_len]
                avg = sum(left)/(date_list_len-end + 1)
                final_val_list.append(avg)
            
            final_date_list = [str(i) for i in range(len(final_val_list))]

            data = {
                'categories': final_date_list,
                'data': final_val_list
            }
            return data
        else:
            return None
    def get(self, request):
        filter = request.GET.get('month', None)
        year_filter = request.GET.get('year', None)
        data = self.get_order_objects(request.user, filter, year_filter)
        if data != None:
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response(data = {'msg':'date or month not provided'}, status=status.HTTP_400_BAD_REQUEST)


class IntDecoratorDetail(APIView):
    permission_classes = [IsAuthenticated]

    def get_user_objects(self, decorator_id):
        return get_object_or_404(CustomUser, id=decorator_id, type=2)

    def get(self, request, decorator_id):
        object = self.get_user_objects(decorator_id)
        serializer = IntDecoratorDetailSerializer(instance=object)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CardDetail(APIView):
    permission_classes = [IsAuthenticated]

    def get_user_object(self, firm_email):
        return get_object_or_404(Firm, user__email=firm_email, user__type=3)

    def get(self, request):
        user = self.get_user_object(request.user)
        serializer = CardDetailSerializer(instance=user)
        return Response(serializer.data, status=status.HTTP_200_OK)

class PurchaseRequestListView(APIView):

    permission_classes = [IsAuthenticated]

    def get_user_object(self, firm_email):
        return get_object_or_404(Firm, user__email=firm_email, user__type=3)

    def get(self,request):
        firm = self.get_user_object(request.user)
        purchase_req = PurchaseRequest.objects.filter(firm=firm).order_by('-created_at')
        remaining = purchase_req.filter(is_rejected=False, is_approved=False).count()
        paginator = CustomPageNumberPagination()
        result_page = paginator.paginate_queryset(purchase_req,request)
        serializer = PurchaseRequestListSerializer(instance=result_page, many=True)
        return Response(data={'data':serializer.data,'remaining':remaining}, status=status.HTTP_200_OK)

class RejectPurchaseRequest(APIView):
    permission_classes = [IsAuthenticated]
    def get_purchase_object(self, pk):
        return get_object_or_404(PurchaseRequest, pk=pk)

    def get(self,request,pk):
        purchase_req =  self.get_purchase_object(pk)
        purchase_req.is_rejected = True
        purchase_req.is_approved = False
        purchase_req.save()
        user = purchase_req.decorator.user
        nt_ins = UserNotifications(user=user, notification_type='purchase-request', text=f"Your purchase request for {purchase_req.items.all().first().product.design.name} is rejected")
        nt_ins.save()
        return Response(data={'msg':'success'}, status=status.HTTP_200_OK)

class AcceptPurchaseRequest(APIView):
    permission_classes = [IsAuthenticated]
    def get_purchase_object(self, pk):
        return get_object_or_404(PurchaseRequest, pk=pk)

    def get(self,request,pk):
        purchase_req =  self.get_purchase_object(pk)
        purchase_req.is_rejected = False
        purchase_req.is_approved= True
        purchase_req.save()
        user = purchase_req.decorator.user
        nt_ins = UserNotifications(user=user, notification_type='purchase-request', text=f"Your purchase request for {purchase_req.items.all().first().product.design.name} is approved")
        nt_ins.save()
        return Response(data={'msg':'success'}, status=status.HTTP_200_OK)



class AddUser(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, referral_code=None):
        print(request.data)
        randompass = ''.join([random.choice('1234567890!@#$%^&*qwertyuiopasdfghjklzxcvbnm') for i in range(7)])
        firm = Firm.objects.get(user__email = request.user)

        fullname = request.data['fullNameKey'].split(' ')
        # firm = request.data.get('registered_firm', None)
        type = ['Artist', 'Interior Decorator']

        data = {}
        data['email'] = request.data['emailKey']
        data['password'] = randompass
        try:
            data['type'] = type.index(request.data['accountTypeKey']) + 1
        except:
            data['type'] = 2
        data['first_name'] = fullname[0]
        data['last_name'] = fullname[1] if len(fullname) >= 2 else ''
        try:
            data['profile_picture'] = request.data['profilePicKey']
        except:
            pass
        data['username'] = request.data['emailKey']
        data['phone'] = request.data['phoneNumberKey']
        data['bio'] = f"-"

        
        reg_serializer = AddUserSerializer(data=data)
        if reg_serializer.is_valid():
            new_user = reg_serializer.save()
            usr = CustomUser.objects.get(pk=new_user.pk)
            firm.members.add(usr)

            try:
                dec = Interior_Decorator.objects.get(user=new_user)
                nt_setting = InteriorDecoratorNotificationSettings(user=dec)
                nt_setting.save()
                dec.level = firm.level
                dec.platinum_commission_percent = firm.platinum_commission_percent
                dec.save()

            except Exception as e:
                print(e)
            user = CustomUser.objects.get(email=usr.email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            current_site = get_current_site(request=request).domain.split(':')[0]
            print(current_site)
            current_site = current_site + '/forgot-password/' + usr.email + '/' + uidb64 + '/' + token
            # relativeLink = reverse('password-reset', kwargs={'uidb64': uidb64, 'token': token})
            absurl = 'http://' + current_site
            email_body = 'Hi ' + user.username + f'\nNew Account is created by {firm.user.email} \nUse the link below to reset your password \nAfter acivation of you account by Wallrus Admin\n' + absurl
            data = {'email_body': email_body,
                    'to_email': user.email,
                    'email_subject': 'Reset your password'}
            send_mail(data)
            try:
                if new_user and request.data['panKey']:

                    business_details = {
                        'user': new_user.pk,
                        'pan_card_number': request.data['panKey'],
                        'brand_name': request.data['organizationKey'],
                        'gst_number': request.data['gstKey'],
                        'phone': new_user.phone,
                        'email': new_user.email
                    }

                    buss_serializer = BusinessDetailSerializer(
                        data=business_details)
                    if buss_serializer.is_valid():
                        buss_serializer.save()
                        
                    else:
                        print(str(buss_serializer.errors))
                        return Response({'error':buss_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            except:
                pass
            

                # if account details were sent create bank details
            try:
                if request.data['accountNumberKey'] and new_user:
                    bank_details = {
                        'user': new_user.pk,
                        'account_number': request.data['accountNumberKey'],
                        'name': request.data['bankNameKey'],
                        'branch': request.data['bankBranchKey'],
                        'swift_code': request.data['swiftCodeKey'],
                        'ifsc_code': request.data['ifscCodeKey']
                    }

                    bank_serializer = BankDetailSerializer(
                        data=bank_details)
                    if bank_serializer.is_valid():
                        bank_serializer.save()
                    else:
                        print(str(bank_serializer.errors))
                        return Response({'error':bank_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            except:
                pass
            return Response({'message': 'Thank you for signing up. Your profile is under review.'},
                                status=status.HTTP_201_CREATED)

        print(str(reg_serializer.errors))
        return Response({'errors':reg_serializer.errors},status=status.HTTP_400_BAD_REQUEST)


class SearchDecoratorView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        keyword = request.GET.get('keyword',None)
        if keyword:
            firm = request.user
            decorators = Firm.objects.get(user__email=firm).members.filter(type=2)
            words = keyword.split(' ')
            query = Q()
            for w in words:
                query |= Q(first_name__icontains=w)
                query |= Q(last_name__icontains=w)
                query |= Q(username__icontains=w)
                query |= Q(email__icontains=w)
            searched_users = decorators.filter(query).distinct()
            paginator = CustomPageNumberPagination()
            result_page = paginator.paginate_queryset(searched_users,request)
            serializer = FirmUserListSerializer(instance=result_page, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"msg":"No Keeyword passed"}, status=status.HTTP_200_OK)


class RemoveUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        pk = request.GET.get('pk', None)
        if pk:
            user = CustomUser.objects.get(pk=pk)
            firm = Firm.objects.get(user=request.user)
            is_member = firm.members.filter(pk = user.pk).exists()
            if is_member:
                firm.members.remove(user)
                return Response({'msg':'success'}, status=status.HTTP_200_OK)
            return Response({'msg':'User does not exits in this firm'}, status= status.HTTP_400_BAD_REQUEST)
        return Response({'msg':'pk (user pk) parameter is required'}, status= status.HTTP_400_BAD_REQUEST)

