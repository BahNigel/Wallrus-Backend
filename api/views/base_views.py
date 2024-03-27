from django.db import models
from django.shortcuts import get_object_or_404
from orders.models import Cart
from invite.models import Invite

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.authentication import BasicAuthentication
from rest_framework import generics

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse 
from django.db.models import Q
from ..utils import send_mail

from users.models import CustomUser, Code, OtpTable
from user_details.models import Address, BankDetail, BusinessDetail
from product.models import Application
from django.contrib.auth import update_session_auth_hash
from ..serializers import *
from notifications.models import *

from ..utils import Encrypt_and_Decrypt, send_mail_otp, send_otp, code_gen, send_admin_mail


class CustomUserCreate(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, referral_code=None):
        print(request.data)

        fullname = request.data['fullNameKey'].split(' ')
        # firm = request.data.get('registered_firm', None)
        type = ['Artist', 'Interior Decorator', 'Organization']

        data = {}
        data['email'] = request.data['emailKey']
        try:
            data['password'] = request.data['passwordKey']
        except:
            data['password'] = BaseUserManager().make_random_password()
        data['type'] = type.index(request.data['accountTypeKey']) + 1
        data['profile_picture'] = request.data['profilePicKey']
        data['first_name'] = fullname[0]
        data['last_name'] = fullname[1] if len(fullname) >= 2 else ''
        data['username'] = request.data['userNameKey']
        data['phone'] = request.data['phoneNumberKey']
        try:
            data['bio'] = request.data['bioKey']
        except:
            data['bio'] = " "

        # TO DO
        # personal_address = {}
        # business_address = {}

        # add_type = ['Personal Address', 'Office Address']

        # Create a new user
        reg_serializer = RegisterUserSerializer(data=data)
        if reg_serializer.is_valid():
            new_user = reg_serializer.save()
            user_ins = CustomUser.objects.get(pk=new_user.pk)
            
            admin_mail_sub = "New User Registered"
            message = f"A new user have joined Wallrus, to approve follow to following url https://thewallruscompany.com:8000/admin/users/customuser/{user_ins.id}/change/"
            send_admin_mail(admin_mail_sub,message)
            if new_user.type == 2:
                create_invite_friend(referral_code, new_user)
                create_cart(new_user)
            
            # new_user = False
            if new_user:

                # Create business details
                business_details = {
                    'user': new_user.pk,
                    'pan_card_number': request.data['panKey'],
                    'brand_name': request.data['organizationKey'],
                    'gst_number': request.data['gstKey'],
                    'phone': request.data['phoneNumberBusinessKey'],
                    'email': request.data['emailBusinessKey']
                }

                buss_serializer = BusinessDetailSerializer(
                    data=business_details)
                if buss_serializer.is_valid():
                    new_buss_details = buss_serializer.save()
                    if new_buss_details:
                        # To Do add business and personal address
                        try:
                            line2 = request.data['addressApartmentAboutyouKey']
                        except:
                            line2 = "-"
                        personal_address = {
                            'user': new_user.pk,
                            'type': 1,
                            'line1': request.data['addressStreetAboutyouKey'],
                            'line2': line2,
                            'city': request.data['addressCityAboutyouKey'],
                            'pincode': request.data['addressPincodeAboutyouKey'],
                            'state': request.data['stateAboutyouKey']

                        }
                        try:
                            line2 = request.data['addressApartmentBusinessKey']
                        except:
                            line2 = "-"
                        business_address = {
                            'user': new_user.pk,
                            'type': 2,
                            'line1': request.data['addressStreetBusinessKey'],
                            'line2': line2,
                            'city': request.data['cityBusinessKey'],
                            'pincode': request.data['pincodeBusinessKey'],
                            'state': request.data['stateBusinessKey']

                        }
                        bussadd_serializer = AddressSerializer(
                            data=business_address)
                        peradd_serializer = AddressSerializer(
                            data=personal_address)
                        print(bussadd_serializer)
                        print(peradd_serializer)
                        if peradd_serializer.is_valid():
                            if bussadd_serializer.is_valid():
                                bussadd_serializer.save()
                                peradd_serializer.save()

                else:
                    user_ins.delete()
                    print(str(buss_serializer.errors))
                    return Response(buss_serializer.errors,status=status.HTTP_400_BAD_REQUEST)

                # if Added through firm 
                try:
                    if request.data['firmUserID']:
                        firm = Firm.objects.get(user__id = request.data['firmUserID'])
                        usr = CustomUser.objects.get(pk=new_user.pk)
                        firm.members.add(usr)
                except:
                    pass

                # if account details were sent create bank details
                if request.data['accountNumberKey']:
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
                        user_ins.delete()
                        print(str(bank_serializer.errors))
                        return Response(bank_serializer.errors,status=status.HTTP_400_BAD_REQUEST)

                return Response({'message': 'Thank you for signing up. Your profile is under review.'},
                                status=status.HTTP_201_CREATED)

        print(str(reg_serializer.errors))
        return Response(reg_serializer.errors,status=status.HTTP_400_BAD_REQUEST)

def create_invite_friend(referral_code, new_user):
    if referral_code is not None:
        referred_by = Invite.objects.get(referral_code=referral_code).user
        print("referred_by:", referred_by)
        print("referred_by type:", type(referred_by))
        Invite.objects.create(user=new_user, referred_by=referred_by)
    else:
        Invite.objects.create(user=new_user)

def create_cart(new_user):
    Cart.objects.create(user=new_user)

class Edit_Detail(APIView):
    '''
    Edit Detail
    '''
    # authentication_classes=[BasicAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_object(self, user_id, model_name, type=1):
        if model_name == Address:
            return model_name.objects.filter(user=user_id, type=type).first()
        return model_name.objects.get(user=user_id)

    def get(self, request, user_id=None, format=None):
        id = request.user.id
        en = Encrypt_and_Decrypt()
        if CustomUser.objects.filter(pk=id, is_active=True).exists():
            user_Businessinfo = self.get_object(id, BusinessDetail)
            user_Basicinfo = CustomUser.objects.get(pk=id)
            user_peradd = self.get_object(id, Address)
            user_busiadd = self.get_object(id, Address, type=2)
            serializer_buss = BusinessDetailSerializer(
                instance=user_Businessinfo)
            serialize_user_basic = RegisterUserSerializer(
                instance=user_Basicinfo)
            serializer_peraddress = AddressSerializer(instance=user_peradd)
            serializer_busiaddress = AddressSerializer(instance=user_busiadd)
            try:
                user_Bankinfo = self.get_object(id, BankDetail)
                serialize_bank = BankDetailSerializer(instance=user_Bankinfo)
                serializer = {'Business_Info': serializer_buss.data,
                              'User_Info': serialize_user_basic.data,
                              'User_Personal_Add_Info': serializer_peraddress.data,
                              'User_Business_Add_Info': serializer_busiaddress.data,
                              'Bank_Info': serialize_bank.data}
                serializer['Bank_Info']['swift_code'] = en.decrypt(
                    serializer['Bank_Info']['swift_code'])
                serializer['Bank_Info']['account_number'] = en.decrypt(
                    serializer['Bank_Info']['account_number'])
            except Exception as e:
                print(">>-----------------",e)
                serializer = {'Business_Info': serializer_buss.data,
                              'User_Info': serialize_user_basic.data, 'User_Personal_Add_Info': serializer_peraddress.data, 'User_Business_Add_Info': serializer_busiaddress.data}
            print(serializer_buss.data)
            try:
                serializer['Business_Info']['pan_card_number'] = en.decrypt(
                    serializer['Business_Info']['pan_card_number'])
                serializer['Business_Info']['gst_number'] = en.decrypt(
                    serializer['Business_Info']['gst_number'])
            except:
                pass
            del serializer['Business_Info']['user']
            del serializer['User_Personal_Add_Info']['user']
            del serializer['User_Business_Add_Info']['user']
            if 'Bank_Info' in serializer:
                del serializer['Bank_Info']['user']
            del en
            return Response(serializer, status=status.HTTP_200_OK)
        else:
            return Response({'status': 'User Doesnot exist'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request):
        print(request.data)
        id = request.user.id
        en = Encrypt_and_Decrypt()
        user_personal = CustomUser.objects.get(pk=id)
        fullname = request.data['fullName'].split(' ')
        data = {}
        if request.data['profilePic'] == '':
            data['profile_picture'] = user_personal.profile_picture
        else:
            data['profile_picture'] = request.data['profilePic']
        data['email'] = user_personal.email
        data['password'] = user_personal.password
        data['type'] = user_personal.type
        data['first_name'] = fullname[0]
        data['last_name'] = fullname[1] if len(fullname) >= 2 else ''
        data['username'] = request.data['userName']
        data['phone'] = request.data['phoneNumber']
        try:
            data['bio'] = request.data['bio']
            if data['bio'] == "":
                data['bio'] == " "
        except:
            data['bio'] = " "
        reg_serializer = RegisterUserSerializer(user_personal, data=data)
        if reg_serializer.is_valid():
            user_status = reg_serializer.save()
            if user_status:
                # Update business details
                buis_detail = BusinessDetail.objects.filter(
                    user=user_personal).first()
                business_details = {
                    'user': user_status.pk,
                    'pan_card_number': en.encrypt(request.data['pan']),
                    'brand_name': request.data['organization'],
                    'gst_number': en.encrypt(request.data['gst']),
                    'phone': request.data['phoneNumberBusiness'],
                    'email': request.data['emailBusiness']
                }
                print(business_details)
                buss_serializer = BusinessDetailSerializer(
                    buis_detail, data=business_details)
                if buss_serializer.is_valid():
                    new_buss_details = buss_serializer.save()
                    if new_buss_details:
                        # To Do add business address
                        buis_add_inst = Address.objects.filter(
                            user=user_personal, type=2).first()
                        pers_add_inst = Address.objects.filter(
                            user=user_personal, type=1).first()
                        try:
                            line2 = request.data['addressApartmentBusiness']
                        except:
                            line2 = "-"
                        business_address = {
                            'user': user_status.pk,
                            'type': 2,
                            'line1': request.data['addressStreetBusiness'],
                            'line2': line2,
                            'city': request.data['cityBusiness'],
                            'pincode': request.data['pincodeBusiness'],
                            'state': request.data['stateBusiness']

                        }
                        try:
                            line2 = request.data['addressApartmentAboutyou']
                        except:
                            line2 = "-"
                        personal_address = {
                            'user': user_status.pk,
                            'type': 1,
                            'line1': request.data['addressStreetAboutyou'],
                            'line2': line2,
                            'city': request.data['addressCityAboutyou'],
                            'pincode': request.data['addressPincodeAboutyou'],
                            'state': request.data['stateAboutyou']

                        }
                        # print(business_address)
                        # bussadd_serializer = AddressSerializer(
                        #     buis_add_inst, data=business_address)
                        # print(bussadd_serializer)
                        # if bussadd_serializer.is_valid():
                        #     bussadd_serializer.save()
                        #     print(bussadd_serializer.save())
                        bussadd_serializer = AddressSerializer(
                            buis_add_inst, data=business_address)
                        peradd_serializer = AddressSerializer(
                            pers_add_inst, data=personal_address)
                        if peradd_serializer.is_valid():
                            if bussadd_serializer.is_valid():
                                bussadd_serializer.save()
                                peradd_serializer.save()

                else:
                    print(str(buss_serializer.errors))
                    return Response(status=status.HTTP_400_BAD_REQUEST)
                Acc_no = en.encrypt(request.data['accountNumber'])
                swift_code = en.encrypt(request.data['swiftCode'])
                # if account details were sent create bank details
                if BankDetail.objects.filter(user=user_personal).first():
                    bank_acc_detail = BankDetail.objects.filter(
                        user=user_personal).first()

                    bank_details = {
                        'user': user_status.pk,
                        'account_number': Acc_no,
                        'name': request.data['bankName'],
                        'branch': request.data['bankBranch'],
                        'swift_code': swift_code,
                        'ifsc_code': request.data['ifscCode']
                    }
                    bank_serializer = BankDetailSerializer(
                        bank_acc_detail, data=bank_details)
                    if bank_serializer.is_valid():
                        bank_serializer.save()
                    else:
                        print(str(bank_serializer.errors))
                        return Response(status=status.HTTP_400_BAD_REQUEST)
                else:
                    bank_details = {
                        'user': user_status.pk,
                        'account_number': request.data['accountNumber'],
                        'name': request.data['bankName'],
                        'branch': request.data['bankBranch'],
                        'swift_code': request.data['swiftCode'],
                        'ifsc_code': request.data['ifscCode']
                    }
                    bank_serializer = BankDetailSerializer(data=bank_details)
                    if bank_serializer.is_valid():
                        bank_serializer.save()
                del en
                return Response({'message': 'Thank you for Updating !!'},
                                status=status.HTTP_201_CREATED)

        print(str(reg_serializer.errors))
        return Response(status=status.HTTP_400_BAD_REQUEST)

class Social_Edit_Detail(APIView):
    '''
    Edit Detail
    '''
    # authentication_classes=[BasicAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_object(self, user_id, model_name, type=1):
        if model_name == Address:
            return model_name.objects.filter(user=user_id, type=type).first()
        return model_name.objects.get(user=user_id)

    def post(self, request):
        # print(request.data)
        type = ['Artist', 'Interior Decorator', 'Organization']
        id = request.user.id
        en = Encrypt_and_Decrypt()
        user_personal = CustomUser.objects.get(pk=id)
        fullname = request.data['fullNameKey'].split(' ')
        data = {}
        if request.data['profilePicKey'] == '':
            data['profile_picture'] = user_personal.profile_picture
        else:
            data['profile_picture'] = request.data['profilePicKey']
        try:
            data['email'] = request.data['emailKey']
            if data['email'] == " " or data['email']=="":
                data['email'] = user_personal.email
        except:
            data['email'] = user_personal.email
        data['password'] = user_personal.password
        data['type'] = type.index(request.data['accountTypeKey']) + 1
        data['first_name'] = fullname[0]
        data['last_name'] = fullname[1] if len(fullname) >= 2 else ''
        data['username'] = request.user.username
        data['phone'] = request.data['phoneNumberKey']
        try:
            data['bio'] = request.data['bioKey']
            if data['bio'] == "":
                data['bio'] == " "
        except:
            data['bio'] = " "
        reg_serializer = RegisterUserSerializer(user_personal, data=data)
        if reg_serializer.is_valid():
            user_status = reg_serializer.save()
            if user_status:
                business_details = {
                    'user': user_status.pk,
                    'pan_card_number': request.data['panKey'],
                    'brand_name': request.data['organizationKey'],
                    'gst_number': request.data['gstKey'],
                    'phone': request.data['phoneNumberBusinessKey'],
                    'email': request.data['emailBusinessKey']
                }
                print(business_details)
                buis_detail = BusinessDetail.objects.filter(user=user_personal)
                if buis_detail.count() == 0:
                    buss_serializer = BusinessDetailSerializer(data=business_details)
                    if buss_serializer.is_valid():
                        new_buss_details = buss_serializer.save()
                # Update business details
                buis_detail = BusinessDetail.objects.filter(
                    user=user_personal).first()
                buss_serializer = BusinessDetailSerializer(
                    buis_detail, data=business_details)
                if buss_serializer.is_valid():
                    new_buss_details = buss_serializer.save()
                    if new_buss_details:
                        # To Do add business address
                        buis_add_inst = Address.objects.filter(
                            user=user_personal, type=2).first()
                        pers_add_inst = Address.objects.filter(
                            user=user_personal, type=1).first()
                        try:
                            line2 = request.data['addressApartmentBusinessKey']
                        except:
                            line2 = "-"
                        business_address = {
                            'user': user_status.pk,
                            'type': 2,
                            'line1': request.data['addressStreetBusinessKey'],
                            'line2': line2,
                            'city': request.data['cityBusinessKey'],
                            'pincode': request.data['pincodeBusinessKey'],
                            'state': request.data['stateBusinessKey']

                        }
                        try:
                            line2 = request.data['addressApartmentAboutyouKey']
                        except:
                            line2 = "-"
                        personal_address = {
                            'user': user_status.pk,
                            'type': 1,
                            'line1': request.data['addressStreetAboutyouKey'],
                            'line2': line2,
                            'city': request.data['addressCityAboutyouKey'],
                            'pincode': request.data['addressPincodeAboutyouKey'],
                            'state': request.data['stateAboutyouKey']

                        }
                        # print(business_address)
                        # bussadd_serializer = AddressSerializer(
                        #     buis_add_inst, data=business_address)
                        # print(bussadd_serializer)
                        # if bussadd_serializer.is_valid():
                        #     bussadd_serializer.save()
                        #     print(bussadd_serializer.save())
                        if buis_add_inst:
                            bussadd_serializer = AddressSerializer(
                                buis_add_inst, data=business_address)
                        else:
                            bussadd_serializer = AddressSerializer(data=business_address)
                        if pers_add_inst:
                            peradd_serializer = AddressSerializer(
                                pers_add_inst, data=personal_address)
                        else:
                            peradd_serializer = AddressSerializer(data=personal_address)
                        if peradd_serializer.is_valid():
                            if bussadd_serializer.is_valid():
                                bussadd_serializer.save()
                                peradd_serializer.save()

                else:
                    print(str(buss_serializer.errors))
                    return Response(buss_serializer.errors,status=status.HTTP_400_BAD_REQUEST)
                Acc_no = en.encrypt(request.data['accountNumberKey'])
                swift_code = en.encrypt(request.data['swiftCodeKey'])
                # if account details were sent create bank details
                if BankDetail.objects.filter(user=user_personal).first():
                    bank_acc_detail = BankDetail.objects.filter(
                        user=user_personal).first()

                    bank_details = {
                        'user': user_status.pk,
                        'account_number': Acc_no,
                        'name': request.data['bankNameKey'],
                        'branch': request.data['bankBranchKey'],
                        'swift_code': swift_code,
                        'ifsc_code': request.data['ifscCode']
                    }
                    bank_serializer = BankDetailSerializer(
                        bank_acc_detail, data=bank_details)
                    if bank_serializer.is_valid():
                        bank_serializer.save()
                    else:
                        print(str(bank_serializer.errors))
                        return Response(bank_serializer.errors,status=status.HTTP_400_BAD_REQUEST)
                else:
                    bank_details = {
                        'user': user_status.pk,
                        'account_number': request.data['accountNumberKey'],
                        'name': request.data['bankNameKey'],
                        'branch': request.data['bankBranchKey'],
                        'swift_code': request.data['swiftCodeKey'],
                        'ifsc_code': request.data['ifscCodeKey']
                    }
                    bank_serializer = BankDetailSerializer(data=bank_details)
                    if bank_serializer.is_valid():
                        bank_serializer.save()
                del en
                user_personal.is_active = False
                user_personal.save()
                return Response({'message': 'Thank you for Updating !!'},
                                status=status.HTTP_201_CREATED)

        print(str(reg_serializer.errors))
        return Response(reg_serializer.errors,status=status.HTTP_400_BAD_REQUEST)


class NotificationSettings(APIView):
    '''
    For the notification settings of a user
    '''
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_object(self, user):
        user = get_object_or_404(CustomUser, is_active=True, email=user)
        return user #get_object_or_404(user_type_notification_model, user=user.id)

    def get(self, request):
        serializer = None
        obj = None
        if request.user.get_type_display() == 'Artist':
            user = self.get_object(request.user)
            user_frm_artist_model = Artist.objects.get(user__id = user.id)
            user_frm_notification_model = ArtistNotificationSettings.objects.filter(user__user__id = user.id)
            l = len(user_frm_notification_model)
            if l==0:
                user_frm_notification_model = ArtistNotificationSettings(user = user_frm_artist_model)
                user_frm_notification_model.save()
            else:
                user_frm_notification_model = user_frm_notification_model[0]
            serializer = ArtistNotificationSettingsSerailizer(instance=user_frm_notification_model)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        
        # Varinder: It is for Decorator
        # if request.user.get_type_display() == 'Decorator':
        #     obj = self.get_object(DecoratorNotificationSetting, request.user)
        #     serializer = DecoratorNotificationSettingSerializer(instance=obj)
        #     return Response(data=serializer.data, status=status.HTTP_200_OK)

        elif request.user.get_type_display() == 'Interior Decorator':
            user = self.get_object(request.user)
            user_frm_decorator_model = Interior_Decorator.objects.get(user__id = user.id)
            user_frm_notification_model = InteriorDecoratorNotificationSettings.objects.filter(user__user__id = user.id)
            l = len(user_frm_notification_model)
            if l==0:
                user_frm_notification_model = InteriorDecoratorNotificationSettings(user = user_frm_decorator_model)
                user_frm_notification_model.save()
            else:
                user_frm_notification_model = user_frm_notification_model[0]
            serializer = InteriorDecoratorNotificationSettingsSerailizer(instance=user_frm_notification_model)
            return Response(data=serializer.data, status=status.HTTP_200_OK)


    def put(self, request):
        serializer = None
        obj = None
        if request.user.get_type_display() == 'Artist':
            user = self.get_object(request.user)
            user_frm_notification_model = ArtistNotificationSettings.objects.filter(user__user__id = user.id)[0]
            serializer = ArtistNotificationSettingsSerailizer(
                instance=user_frm_notification_model, data=request.data)
        elif request.user.get_type_display() == 'Interior Decorator':
            user = self.get_object(request.user)
            user_frm_notification_model = InteriorDecoratorNotificationSettings.objects.filter(user__user__id = user.id)[0]
            serializer = InteriorDecoratorNotificationSettingsSerailizer(
                instance=user_frm_notification_model, data=request.data)

        # Varinder: It is for Decorator
        # if request.user.get_type_display() == 'Decorator':
        #     obj = self.get_object(DecoratorNotificationSetting, request.user)
        #     serializer = DecoratorNotificationSettingSerializer(
        #         instance=obj, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK)

        return Response(status=status.HTTP_400_BAD_REQUEST)

# class DecoratorNotificationSetting(APIView):


class ChangePasswordView(APIView):
    """
    An endpoint for changing password.
    """
    # authentication_classes=[BasicAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_object(self, queryset=None):
        return self.request.user

    def put(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = ChangePasswordSerializer(data=request.data, partial=True)
        try:
            if request.data["password1"] and request.data["password2"] and request.data['password']:
                pass
        except:
            return Response({"Password": ["Error (Password Field is empty)"]},
                            status=status.HTTP_400_BAD_REQUEST)
        if serializer.is_valid():
            old_password = serializer.data.get("password")
            print(self.object.check_password(old_password))
            if not self.object.check_password(old_password):
                return Response({"old_password": ["Wrong password."]},
                                status=status.HTTP_400_BAD_REQUEST)

            else:
                if request.data["password1"] == request.data["password2"] and request.data["password"] == request.data["password1"]:
                    return Response({"New Password": ["Same as Old Password"]},
                                    status=status.HTTP_400_BAD_REQUEST)

                elif request.data["password1"] == request.data["password2"]:
                    self.object.set_password(request.data["password1"])
                    self.object.save()
                    return Response(status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AppList(APIView):
    '''
    Fetch List of Applications
    '''

    def get(self, request):
        list = Application.objects.filter(is_active=True)
        serializer = ApplistSerializer(instance=list, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class UserTypeView(APIView):
    '''
    User Type
    '''
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request, user_id=None, format=None):
        user_Basicinfo = CustomUser.objects.get(pk=request.user.id)
        serializer_type = UserTypeSerializer(instance=user_Basicinfo)
        return Response(data=serializer_type.data, status=status.HTTP_200_OK)


class VerifyUserView(APIView):
    # authentication_classes=[BasicAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        user = CustomUser.objects.get(pk=request.user.id)
        OTP = request.data["OTP"]
        code = Code.objects.get(user=user)
        if str(code.number) == OTP:
            code.save()
            return Response(data="VERIFIED", status=status.HTTP_200_OK)
        else:
            return Response(data="NOT VERIFIED", status=status.HTTP_401_UNAUTHORIZED)


class SendOTPView(APIView):
    # authentication_classes=[BasicAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        user = CustomUser.objects.get(pk=request.user.id)
        choice = request.data["choice"]
        email = user.email
        Code.objects.get(user=user).save()
        code = Code.objects.get(user=user).number
        phone_number = user.phone
        if choice == 'mobile':
            msg = 'Hii ! Your Verication Code for Login to Wallrus is ' + \
                str(code)+'.'
            send_otp(phone_number, msg)
            return Response(data="OTP Sent", status=status.HTTP_200_OK)
        elif choice == 'mail':
            msg = "Hii ! Your Verication Code for Login to Wallrus is " + code + "."
            send_mail_otp(email, msg)
            return Response(data="OTP Sent", status=status.HTTP_200_OK)


class EmailPhoneView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        choice = request.data["choice"]
        value = request.data["value"]
        code = code_gen()
        otp_ins = OtpTable(otp=code)
        otp_ins.save()
        if choice == 'sms':
            exists = CustomUser.objects.filter(phone=value).exists()
            if exists:
                return Response(data={'msg':"user already exists with this email"}, status=status.HTTP_400_BAD_REQUEST)
            msg = str(code) + " is the OTP for signing up on the Wallrus platform."
            send_otp(value, msg)
            return Response(data={'otp_id':otp_ins.id}, status=status.HTTP_200_OK)
        elif choice == 'email':
            exists = CustomUser.objects.filter(email=value).exists()
            if exists:
                return Response(data={'msg':"user already exists with this email"}, status=status.HTTP_400_BAD_REQUEST)
            msg = str(code) + " is the OTP for signing up on the Wallrus platform."
            send_mail_otp(value, msg)
            return Response(data={'otp_id':otp_ins.id}, status=status.HTTP_200_OK)

class ValidateOtpView(APIView):
    def post(self,request):
        otp_id = request.data['otp_id']
        otp = request.data['otp']
        try:
            otp_ins = OtpTable.objects.get(id=otp_id)
            if str(otp_ins.otp) == str(otp):
                otp_ins.delete()
                return Response(data={'msg':'success'}, status=status.HTTP_200_OK)
            return Response(data={'msg':'wrong otp'}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response(data={'msg':'wrong otp id'}, status=status.HTTP_400_BAD_REQUEST)


class RequestPasswordResetEmail(generics.GenericAPIView):
    serializer_class =ResetPasswordEmailRequestSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        
        email = request.data['email']
        
        if CustomUser.objects.filter(email=email).exists():
            user = CustomUser.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            current_site = get_current_site(request=request).domain.split(':')[0]
            print(current_site)
            current_site = current_site + '/forgot-password/' + email + '/' + uidb64 + '/' + token 
            # relativeLink = reverse('password-reset', kwargs={'uidb64': uidb64, 'token': token})
            absurl = 'http://' + current_site
            email_body = 'Hi ' + user.username + '\n Use the link below to reset your password \n' + absurl
            data = {'email_body': email_body,
                    'to_email': user.email,
                    'email_subject': 'Reset your password'}
            send_mail(data)
        
            return Response({'message': 'We have sent you a link to reset your password', 'uidb64': uidb64, 'token': token}, status=status.HTTP_200_OK)

        return Response({'message': 'No matching user'}, status= status.HTTP_400_BAD_REQUEST)

class PasswordTokenCheckAPI(generics.GenericAPIView):
    def get(self, request, uidb64, token):
        try:
            id=smart_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(id=id)
            
            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({'error': 'Token is not valid, please request a new token'}, status=status.HTTP_401_UNAUTHORIZED)
        
            return Response({'success': True, 'message':'Credentials valid', 'uidb64': uidb64, 'token':token}, status=status.HTTP_200_OK)

        except DjangoUnicodeDecodeError as identifier:
            return Response({'error': 'Tokenis not valid, please request a new token'}, status=status.HTTP_401_UNAUTHORIZED)
        
class SetNewPassswordAPIView(generics.GenericAPIView):
    serializer_class = SetNewPassswordSerializer

    def patch(self, request):
        try:
            uid64 = request.data['uidb64']
            id=smart_str(urlsafe_base64_decode(uid64))
            token = request.data['token']
            user = CustomUser.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({'error': 'Token is not valid, please request a new token'}, status=status.HTTP_401_UNAUTHORIZED)
            
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid(raise_exception=True):
                user.set_password(request.data['password'])
                user.save()
                return Response({'success': True, 'message': 'Password reset successful'}, status=status.HTTP_200_OK)

        except DjangoUnicodeDecodeError as identifier:
            return Response({'error': 'Tokenis not valid, please request a new token'}, status=status.HTTP_401_UNAUTHORIZED)
        

class SubscribeNewsLetter(APIView):

    def post(self,request):
        email = request.POST.get('email')
        ins = NewsLetterSubscribers(email= email)
        ins.save()
        return Response(data='Subscribed', status=status.HTTP_201_CREATED)

class AddAddress(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        addrs = Address.objects.filter(user = request.user.pk).order_by('-pk')
        print(request.user.pk)
        if addrs.count() > 0:
            addr = addrs[0]
            serializer = AddressSerializer(instance=addr)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'msg':'No address available'}, status=status.HTTP_400_BAD_REQUEST)

    def post(self,request):
        ADDRESS_TYPE = [
                'Personal Address',
                'Business Address',
                'Shipping Address',
                'Billing Address',
                'Installation Address'
            ]
        personal_address = {
                'user': request.user.pk,
                'type': ADDRESS_TYPE.index(request.data['addressTypeKey']) +1,
                'line1': request.data['addressStreetAboutyouKey'],
                'line2': request.data['addressApartmentAboutyouKey'],
                'city': request.data['addressCityAboutyouKey'],
                'pincode': request.data['addressPincodeAboutyouKey'],
                'state': request.data['stateAboutyouKey']

            }
        peradd_serializer = AddressSerializer(
                            data=personal_address)
        if peradd_serializer.is_valid() :
            peradd_serializer.save()
            return Response(data=peradd_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({'error':peradd_serializer.errors},status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request):
        ADDRESS_TYPE = [
                'Personal Address',
                'Business Address',
                'Shipping Address',
                'Billing Address',
                'Installation Address'
            ]
        personal_address = {
                'user': request.user.pk,
                'type': ADDRESS_TYPE.index(request.data['addressTypeKey']) +1,
                'line1': request.data['addressStreetAboutyouKey'],
                'line2': request.data['addressApartmentAboutyouKey'],
                'city': request.data['addressCityAboutyouKey'],
                'pincode': request.data['addressPincodeAboutyouKey'],
                'state': request.data['stateAboutyouKey']

            }
        address = Address.objects.get(pk=request.data['pk'])
        peradd_serializer = AddressSerializer(address,
                            data=personal_address)
        if peradd_serializer.is_valid() :
            peradd_serializer.save()
            return Response(data=peradd_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({'error':peradd_serializer.errors},status=status.HTTP_400_BAD_REQUEST)

class GlobalSearchView(APIView):

    def get(self,request):
        keyword = request.GET.get('keyword',None)
        if keyword:
            words = keyword.split(' ')
            query_u = Q()
            for w in words:
                query_u |= Q(first_name__icontains=w)
                query_u |= Q(last_name__icontains=w)
                query_u |= Q(username__icontains=w)
                query_u |= Q(email__icontains=w)
            searched_users = CustomUser.objects.filter(is_active=True).filter(query_u).distinct()
            user_serializer = SearchUserSerializer(instance=searched_users, many=True)

            query_product = Q()
            for w in words:
                query_product |= Q(application__name__icontains=w)
                query_product |= Q(design__name__icontains=w)
                query_product |= Q(tags__name__icontains=w)
            searched_products = Product.objects.filter(is_active=True).filter(query_product).distinct()
            product_serializer = SearchProductListSerializer(instance=searched_products, many=True)

            query_post = Q()
            for w in words:
                query_post |= Q(title__icontains=w)
            searched_posts = Post.objects.filter(query_post).distinct()
            post_serializer = SearchPostSerializer(instance=searched_posts, many=True)

            return Response({'users':user_serializer.data,'products':product_serializer.data,'posts':post_serializer.data}, status=status.HTTP_200_OK)
        return Response({'users':[],'products':[],'posts':[]}, status=status.HTTP_200_OK)



class SocilaUserDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = SocialUserDetailsSerializer(instance=user)
        return Response(data=serializer.data, status=status.HTTP_200_OK)