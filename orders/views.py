from email.policy import HTTP
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from rest_framework.permissions import IsAuthenticated, AllowAny
from notifications.models import UserNotifications
from product.models import Coupon, Product, Material

from orders.serializer import CartSerializer, ClientCartSerializer, ClientViewCartSerializer, ItemSerializer, ItemListSerializer, CouponDetailsSerializer, ClientDetailsSerializer
from orders.models import Cart, ClientCart, ClientDetails, PurchaseRequest, Refund

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.db.models import Sum
import razorpay
import random
from api.custom_pagination import CustomPageNumberPagination

from users.models import CustomUser, Firm, Interior_Decorator, Artist
from orders.models import Item, Order, Cart, InstallationRequest, OrderStatus
from user_details.models import Address, CoinTransaction
from api.serializers import OrderDetailSerializer, AddressSerializer
from api.utils import send_mail, send_otp, send_admin_mail

class CouponDetails(APIView):

    def get(self,request):
        code = request.GET.get('code',None)
        if code is not None:
            objs = Coupon.objects.filter(code=code)
            if objs.count() > 0:
                coupon = objs[0]
                if coupon.is_onetime and coupon.is_used:
                    return Response({'msg':'Coupon already used'}, status=status.HTTP_400_BAD_REQUEST)
                serializer = CouponDetailsSerializer(instance=coupon)
                return Response(serializer.data,status=status.HTTP_200_OK)
            return Response({'msg':'Coupon Code Not Found'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'msg':'No code sent'}, status=status.HTTP_400_BAD_REQUEST)

class CreateDiscoutCoupon(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        amount = request.data['amount']
        criteria = 'substract'
        user = Interior_Decorator.objects.get(user=request.user)
        available_points = user.reward_points
        if float(available_points) >= float(amount):
            count =0
            block = 0
            while count < 10 and block == 0:
                code = ''.join([random.choice('1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZqwertyuiopasdfghjklzxcvbnm') for i in range(8)])
                count += 1
                if not Coupon.objects.filter(code=code).exists():
                    block = 1
                    break
            ins = Coupon(user= request.user, code = code, application_criteria=criteria, off_value=int(amount), is_onetime=True)
            ins.save()
            user.reward_points = user.reward_points - int(amount)
            user.save()

            return Response({'msg':'Coupon Created','coupon_code':code}, status=status.HTTP_201_CREATED)
        return Response({'msg':'Not enough balance'}, status=status.HTTP_400_BAD_REQUEST)

class CartView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CartSerializer

    # * Unit Conversion Functions

    def cm_to_m(self,cm):
        return cm/100

    def cm_to_inch(self,cm):
        return cm/2.54

    def ft_to_m(self,ft):
        return ft/3.281
    
    def ft_to_inch(self,ft):
        return ft* 12
    
    def mm_to_inch(self,mm):
        cm = mm/10
        return self.cm_to_inch(cm)
    

    # *Pricing Calculator logic - https://docs.google.com/document/d/1eN4UNJQdMeNHX9mayExe-bYVFsmiPTls/edit
    def calculate_price_1(self,unit,height,width,sqft_price):
        """Wallpapers, Wall & Furniture Decals, Glass Films
        """
        if unit == 'cm':
            height = self.cm_to_inch(height)
            width = self.cm_to_inch(width)
        elif unit == 'ft':
            height = self.ft_to_inch(height)
            width = self.ft_to_inch(width)
        elif unit == 'mm':
            height = self.mm_to_inch(height)
            width = self.mm_to_inch(width)
        elif unit == 'in':
            pass
        
        sqft = (height*width)/144
        cost = sqft * sqft_price
        return cost

    def calculate_price_2(self,unit,height,width,mtr_price):
        """Curtains
        """
        if unit == 'cm':
            height = self.cm_to_inch(height)
            width = self.cm_to_inch(width)
        elif unit == 'ft':
            height = self.ft_to_inch(height)
            width = self.ft_to_inch(width)
        elif unit == 'mm':
            height = self.mm_to_inch(height)
            width = self.mm_to_inch(width)
        elif unit == 'in':
            pass

        panel_count = width/22
        panel_height_mtr = (height + 12)/39
        required_material = panel_height_mtr * panel_count
        cost = required_material * mtr_price
        return cost

    def calculate_price_3(self,unit,height,width,sqft_price,channel_price):
        """Frames
        """
        if unit == 'cm':
            height = self.cm_to_inch(height)
            width = self.cm_to_inch(width)
        elif unit == 'ft':
            height = self.ft_to_inch(height)
            width = self.ft_to_inch(width)
        elif unit == 'mm':
            height = self.mm_to_inch(height)
            width = self.mm_to_inch(width)
        elif unit == 'in':
            pass

        cost =(width * channel_price)+ (height * channel_price) + ((height*width)/144) * sqft_price
        return cost

    def get(self, request, pk=None, format=None):
        context = {'request': request}
        if pk is not None:
            obj = Item.objects.get(id=pk)
            serializer = ItemListSerializer(obj, context = {'request': request})
            return Response(serializer.data, status = status.HTTP_200_OK)

        try:
            cart = Cart.objects.get(user=request.user)
        except:
            cart = Cart(user = request.user)
            cart.save()
        serializer = CartSerializer(cart, context = {'request': request})
        return Response(serializer.data, status = status.HTTP_200_OK)

    def post(self, request, format=None):
        try:
            cart = Cart.objects.get(user=request.user)
        except:
            cart = Cart(user = request.user)
            cart.save()
        
        decorator = Interior_Decorator.objects.get(user=request.user)
        unit = request.data['unit']
        height = float(request.data['height'])
        width = float(request.data['width'])
        product = Product.objects.get(sku=request.data['product'])
        material = request.data['material']
        material = Material.objects.get(pk = int(material))
        pricing_category = product.application.pricing_category
        if pricing_category == "category-1" :
            cost_p_product = self.calculate_price_1(unit,height,width,material.unit_price)
        elif pricing_category == "category-2" :
            cost_p_product = self.calculate_price_2(unit,height,width,material.unit_price)
        elif pricing_category == "category-3" :
            cost_p_product = self.calculate_price_3(unit,height,width,material.unit_price,material.unit_price_2)

        cost_p_product = cost_p_product + cost_p_product* product.get_royalty()/100 + cost_p_product *decorator.get_commision_percent()/100
        backend_price = cost_p_product * int(request.data['quantity'])
        print(backend_price)
        if int(backend_price) == int(float(request.data['price'])):
            item_details = {
            'product' : request.data['product'],
            'quantity' : int(request.data['quantity']),
            'width' : width,
            'height' : height,
            'unit' : request.data['unit'],
            'material' : material.pk,
            'price' : int(backend_price),
            'cart' : cart.pk,
            }   

            item_serializer = ItemSerializer(data=item_details)
            if item_serializer.is_valid():
                item = item_serializer.save() 
                return Response({"message": "Success! The Item has been added to the user's cart."}, status = status.HTTP_201_CREATED)
            return Response(item_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": f"Price did not matched - {backend_price}"}, status = status.HTTP_400_BAD_REQUEST)
        
    def put(self, request, pk, format=None):
        obj = Item.objects.get(id=pk)
        unit = request.data['unit']
        height = float(request.data['height'])
        width = float(request.data['width'])
        product = Product.objects.get(sku=request.data['product'])
        pricing_category = product.application.pricing_category

        if pricing_category == "category-1" :
            cost_p_product = self.calculate_price_1(unit,height,width,product.get_base_cost())
        elif pricing_category == "category-2" :
            cost_p_product = self.calculate_price_2(unit,height,width,product.get_base_cost())
        elif pricing_category == "category-3" :
            cost_p_product = self.calculate_price_3(unit,height,width,product.get_base_cost(),product.cost_2)

        backend_price = cost_p_product * int(request.data['quantity'])
        print(backend_price)

        if int(backend_price) == int(float(request.data['price'])):
            item_details = {
            'product' : request.data['product'],
            'quantity' : int(request.data['quantity']),
            'width' : width,
            'height' : height,
            'unit' : request.data['unit'],
            'material' : Material.objects.get(pk = int(request.data['material'])).pk,
            'price' : int(backend_price),
            } 
            serializer = ItemSerializer(obj, data=item_details)
            if serializer.is_valid():
                serializer.save()
                return Response({"message":"Success! The Item has been updated."}, status=status.HTTP_202_ACCEPTED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": f"Price did not matched - {backend_price}"}, status = status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        try:
            item = Item.objects.get(pk=pk)
            item.delete()
            return Response({'msg':'Success'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error':e}, status=status.HTTP_400_BAD_REQUEST)

class ClientDetailsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        clients = ClientDetails.objects.filter(decorator=request.user)
        paginator = CustomPageNumberPagination()
        result_page = paginator.paginate_queryset(clients,request)
        serializers = ClientDetailsSerializer(instance=result_page,many=True, context = {'request': request})
        return Response(data=serializers.data, status=status.HTTP_200_OK)


class ShareCart(APIView):

    permission_classes = [IsAuthenticated]

    def get(self,request):
        clients = ClientDetails.objects.filter(decorator=request.user)
        carts = ClientCart.objects.filter(client__in=clients).exclude(items=None)
        paginator = CustomPageNumberPagination()
        result_page = paginator.paginate_queryset(carts,request)
        serializers = ClientCartSerializer(instance=result_page,many=True, context = {'request': request})
        return Response(data=serializers.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        client_contact = request.data['contactKey']
        try:
            desc = request.data['descriptionKey']
        except:
            desc = None
        cart = Cart.objects.get(user=request.user)
        if Item.objects.filter(cart=cart).count() == 0:
            return Response({'msg':"No Item in cart"}, status= status.HTTP_400_BAD_REQUEST)

        client = ClientDetails.objects.filter(contact=client_contact,decorator=request.user)
        if client.count() >0:
            client_obj = client[0]
        else:
            client_obj = ClientDetails(contact=client_contact,decorator=request.user)
            client_obj.save()
        client_cart = ClientCart(client=client_obj,description=desc)
        client_cart.save()
        for item in Item.objects.filter(cart=cart):
            client_cart.items.add(item)
            item.cart = None
            item.save()
        current_site = get_current_site(request=request).domain.split(':')[0]
        print(current_site)
        link ='http://' + current_site + f"/shared/{client_obj.pk}/{client_cart.pk}"

        msg = f"Hi, Interior decorator-{request.user.first_name} {request.user.last_name} shared some products with you can proceed to payment by clicking the link below. \n {link}"
        if len(client_contact.split('@')) == 2:
            data = {
                'email_subject':"Wallrus: Cart Shared",
                'email_body':msg,
                'to_email':client_contact
            }
            send_mail(data)
        else:
            send_otp(client_contact,msg)
        return Response({"link":link}, status=status.HTTP_201_CREATED)
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class InitiateOrder(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        amount = float(request.data['amount'])
        print(request.user)
        user = CustomUser.objects.get(email= request.user)
        decorator = Interior_Decorator.objects.get(user=user)
        cart = Cart.objects.get(user=user)
        items = Item.objects.filter(cart=cart)
        if items.count() < 1 :
            return Response({'msg':'No Item in Cart'}, status=status.HTTP_400_BAD_REQUEST)
        backend_price = cart.get_total_price()
        try:
            code = request.data['coupon_code']
            if len(code) > 7:
                objs = Coupon.objects.filter(code=code)
                if objs.count() > 0:
                    coupon = objs[0]
                    if (coupon.is_onetime and not coupon.is_used) or not coupon.is_onetime:
                        if coupon.application_criteria == 'percentage':
                            backend_price = backend_price - backend_price * (coupon.off_value / 100)
                        else:
                            backend_price = backend_price - coupon.off_value
                    else:
                        return Response({'msg':'Coupon Expired'}, status=status.HTTP_400_BAD_REQUEST)
        except:
            pass
        is_coins = request.data['is_coins'] == "YES"
        if is_coins:
            coins = int(request.data['coins'])
            backend_price = backend_price - coins
            print(coins, decorator.reward_points)
            if decorator.reward_points < coins:
                return Response({'msg':'not enough coins'}, status=status.HTTP_400_BAD_REQUEST)
        if int(backend_price) == int(amount):
            try:
                client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID,settings.RAZORPAY_KEY_SECRET))

                DATA = {
                    "amount": int(amount*100),
                    "currency": "INR",
                    "payment_capture":1
                    }
                    
                payment_order = client.order.create(data=DATA)                   
                                    
                return Response({
                    'status': "Success",
                    'amount':amount,
                    'api_key':settings.RAZORPAY_KEY_ID,
                    'order_id':payment_order['id'],
                    'payment_order_status':payment_order['status']
                    }, status=status.HTTP_200_OK)
            
            except Exception as e:
                return Response({'status': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'status': 'price not matched'}, status=status.HTTP_400_BAD_REQUEST)

class PlaceOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # try:
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID,settings.RAZORPAY_KEY_SECRET))
        razorpay_order_id = request.data['razorpay_order_id']
        razorpay_payment_id = request.data['razorpay_payment_id']
        razorpay_signature = request.data['razorpay_signature']
        data = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }
        check = None #client.utility.verify_payment_signature(data)
        if check is None:
            user = CustomUser.objects.get(email= request.user)
            decorator = Interior_Decorator.objects.get(user=user)
            cart = Cart.objects.get(user=user)
            items = Item.objects.filter(cart=cart)
            amount = float(request.data['amount'])
            backend_price = cart.get_total_price()
            backend_price1 = cart.get_total_price()
            try:
                shipping_address_id = int(request.data['shipping_address_id'])
                shipping_address = Address.objects.get(id = shipping_address_id)
            except:
                shipping_address = Address.objects.filter(user = user)[0]

            try:
                billing_address_id = int(request.data['billing_address_id'])
                billing_address = Address.objects.get(id = billing_address_id)
            except:
                billing_address = Address.objects.filter(user = user)[0]
            is_installationrequest = request.data['is_installation_request'] == "YES"

            try:
                code = request.data['coupon_code']
                if len(code) > 7:
                    objs = Coupon.objects.filter(code=code)
                    if objs.count() > 0:
                        coupon = objs[0]
                        if (coupon.is_onetime and not coupon.is_used) or not coupon.is_onetime:
                            coupon.is_used = True
                            coupon.save()
                            if coupon.application_criteria == 'percentage':
                                backend_price = backend_price - backend_price * (coupon.off_value / 100)
                            else:
                                backend_price = backend_price - coupon.off_value
            except:
                pass

            is_coins = request.data['is_coins'] == "YES"
            if is_coins:
                coins = int(request.data['coins'])
                backend_price = backend_price - coins
                if decorator.reward_points < coins:
                    return Response({'msg':'not enough coins'}, status=status.HTTP_400_BAD_REQUEST)
                decorator.reward_points = decorator.reward_points - coins
                decorator.save()
            else:
                coins = 0
            if int(amount) == int(backend_price) :
                order = Order(user = user, order_cost = backend_price1, billing_address = billing_address,
                        shipping_address= shipping_address)
                order.save()
                admin_mail_sub = f"New order placed by {request.user.email}"
                message = f"A new order has been placed, details: https://thewallruscompany.com:8000/admin/orders/order/{order.id}/change/"
                send_admin_mail(admin_mail_sub,message)
                reward = backend_price1*(decorator.level.commission_percent/100)
                decorator.reward_points = decorator.reward_points + reward
                decorator.save()

                if is_installationrequest :
                    try:
                        install_name = request.data['installation_name']
                        install_phone = request.data['installation_phone']
                        install_email = request.data['installation_email']
                        install_address_id = int(request.data['installation_req_addr_id'])
                    except:
                        install_name = f"{user.first_name} {user.last_name}"
                        install_phone = user.phone
                        install_email = user.email
                        install_address_id = shipping_address_id
                    install_address = Address.objects.get(id = install_address_id)
                    ins = InstallationRequest(user = user, name = install_name, phone =install_phone, email = install_email, address = install_address)
                    ins.save()
                    admin_mail_sub = f"New installation request by {request.user.email}"
                    message = f"A new order has been placed, details: https://thewallruscompany.com:8000/admin/orders/order/{order.id}/change/"
                    send_admin_mail(admin_mail_sub,message)


                for item in items:
                    print(item)
                    item.order = order
                    item.cart = None
                    item.save()
                    artist_earning = item.product.design.artist.artist.get_royalty_percent()*item.price/100
                    artist = Artist.objects.get(user=item.product.design.artist)
                    artist.earnings = artist.earnings + artist_earning
                    artist.save()
                    nt_ins2 = UserNotifications(user=item.product.design.artist, notification_type='design_purchase', text=f"{user.first_name} {user.last_name} Purchased {item.product.design.name}")
                    nt_ins2.save()

                order_status = OrderStatus(order=order, name = 'pending')
                order_status.save()
                if coins >0 :
                    ct_ins = CoinTransaction(user=user,description = f"For using in order(id:{order.pk}) ", amount=int(amount),debit=coins)
                    ct_ins.save()
                ct_ins1 = CoinTransaction(user=user,description = f"For using in order(id:{order.pk}) ", amount=int(amount),credit=reward)
                ct_ins1.save()

                serializer = OrderDetailSerializer(instance = order)

                return Response(data = serializer.data, status= status.HTTP_200_OK)

            else:
                return Response({'msg':'Price not matched'}, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response({'status': "Not verified"}, status=status.HTTP_400_BAD_REQUEST)
    
        # except Exception as e:
        #     return Response({'status': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class AddPurchaseRequest(CartView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        decorator = Interior_Decorator.objects.get(user=request.user)
        firm = Firm.objects.get(members=request.user)
        unit = request.data['unit']
        height = float(request.data['height'])
        width = float(request.data['width'])
        product = Product.objects.get(sku=request.data['product'])
        material = request.data['material']
        material = Material.objects.get(pk = int(material))
        pricing_category = product.application.pricing_category
        try:
            client_name = request.data['client_name']
        except:
            client_name = None

        if pricing_category == "category-1" :
            cost_p_product = self.calculate_price_1(unit,height,width,material.unit_price)
        elif pricing_category == "category-2" :
            cost_p_product = self.calculate_price_2(unit,height,width,material.unit_price)
        elif pricing_category == "category-3" :
            cost_p_product = self.calculate_price_3(unit,height,width,material.unit_price,material.unit_price_2)
        cost_p_product = cost_p_product + cost_p_product* product.get_royalty()/100 + cost_p_product *decorator.get_commision_percent()/100
        backend_price = cost_p_product * int(request.data['quantity'])
        print(backend_price)

        if int(backend_price) == int(float(request.data['price'])):
            item_details = {
            'product' : request.data['product'],
            'quantity' : int(request.data['quantity']),
            'width' : width,
            'height' : height,
            'unit' : request.data['unit'],
            'material' : material.pk,
            'price' : int(backend_price),
            }   

            item_serializer = ItemSerializer(data=item_details)
            if item_serializer.is_valid():
                item = item_serializer.save() 
                print(item)
                pr = PurchaseRequest(decorator=decorator, firm=firm, price = backend_price, client_name=client_name)
                pr.save()
                pr.items.add(item)
                return Response({"message": "Success! The Item has been added to the user's cart."}, status = status.HTTP_201_CREATED)
            return Response(item_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": f"Price did not matched - {backend_price}"}, status = status.HTTP_400_BAD_REQUEST)


        
# * Client Views Not authorized

class ClientCartView(APIView):

    def get(self,request):
        client_pk = request.GET.get('client')
        cart_pk = request.GET.get('cart')
        client = ClientDetails.objects.get(pk=client_pk)
        cart = ClientCart.objects.get(pk=cart_pk)

        if cart.client.pk == client.pk:
            serializer = ClientViewCartSerializer(instance=cart)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'msg':"cart and client didn't match"}, status=status.HTTP_400_BAD_REQUEST)


class InitiateClientOrder(APIView):

    def post(self, request):
        amount = float(request.data['amount'])
        cart_pk = request.data['cart']
        cart = ClientCart.objects.get(pk=cart_pk)
        backend_price = cart.items.all().aggregate(Sum('price'))['price__sum']
        try:
            code = request.data['coupon_code']
            if len(code) > 7:
                objs = Coupon.objects.filter(code=code)
                if objs.count() > 0:
                    coupon = objs[0]
                    if (coupon.is_onetime and not coupon.is_used) or not coupon.is_onetime:
                        if coupon.application_criteria == 'percentage':
                            backend_price = backend_price - backend_price * (coupon.off_value / 100)
                        else:
                            backend_price = backend_price - coupon.off_value
        except:
            pass
        if int(backend_price) == int(amount):
            try:
                client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID,settings.RAZORPAY_KEY_SECRET))

                DATA = {
                    "amount": int(backend_price*100),
                    "currency": "INR",
                    "payment_capture":1
                    }
                    
                payment_order = client.order.create(data=DATA)                   
                                    
                return Response({
                    'status': "Success",
                    'amount':amount,
                    'api_key':settings.RAZORPAY_KEY_ID,
                    'order_id':payment_order['id'],
                    'payment_order_status':payment_order['status']
                    }, status=status.HTTP_200_OK)
            
            except Exception as e:
                return Response({'status': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'msg':"Price didn't match"}, status=status.HTTP_400_BAD_REQUEST)

class ClientPlaceOrderView(APIView):

    def post(self, request):
        # try:
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID,settings.RAZORPAY_KEY_SECRET))
        razorpay_order_id = request.data['razorpay_order_id']
        razorpay_payment_id = request.data['razorpay_payment_id']
        razorpay_signature = request.data['razorpay_signature']
        data = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }
        check = client.utility.verify_payment_signature(data)
        if check is None:
            cart = ClientCart.objects.get(pk=request.data['cart'])
            user = cart.client.decorator
            items = cart.items.all()
            amount = float(request.data['amount'])
            backend_price = cart.get_total_price()
            backend_price1 = cart.get_total_price()
            try:
                shipping_address_id = int(request.data['shipping_address_id'])
                shipping_address = Address.objects.get(id = shipping_address_id)
            except:
                try:
                    shipping_address = Address.objects.filter(user = user)[0]
                except:
                    shipping_address = None

            try:
                billing_address_id = int(request.data['billing_address_id'])
                billing_address = Address.objects.get(id = billing_address_id)
            except:
                try:
                    billing_address = Address.objects.filter(user = user)[0]
                except:
                    billing_address = None

            try:
                code = request.data['coupon_code']
                if len(code) > 7:
                    objs = Coupon.objects.filter(code=code)
                    if objs.count() > 0:
                        coupon = objs[0]
                        if (coupon.is_onetime and not coupon.is_used) or not coupon.is_onetime:
                            coupon.is_used = True
                            coupon.save()
                            if coupon.application_criteria == 'percentage':
                                backend_price = backend_price - backend_price * (coupon.off_value / 100)
                            else:
                                backend_price = backend_price - coupon.off_value
            except:
                pass
            order = Order(user = user, order_cost = backend_price1 , billing_address = billing_address,
                    shipping_address= shipping_address)
            order.save()
            decorator = Interior_Decorator.objects.get(user = cart.client.decorator)

            admin_mail_sub = f"New order placed by {decorator.user.email}"
            message = f"A new order has been placed, details: https://thewallruscompany.com:8000/admin/orders/order/{order.id}/change/"
            send_admin_mail(admin_mail_sub,message)

            reward = backend_price1*(decorator.level.commission_percent/100)
            decorator.reward_points = decorator.reward_points + reward
            decorator.save()
            ct_ins1 = CoinTransaction(user=user,description = f"For using in order(id:{order.pk}) ", amount=int(amount),credit=reward)
            ct_ins1.save()
            nt_ins = UserNotifications(user=user, notification_type='order', text=f"Your Client, {cart.client.contact}, have placed a order(id:{order.pk}).")
            nt_ins.save()
            try:
                is_installationrequest = request.data['is_installation_request'] == "YES"
                if is_installationrequest :
                    install_name = request.data['installation_name']
                    install_phone = request.data['installation_phone']
                    install_email = request.data['installation_email']
                    install_address_id = int(request.data['installation_req_addr_id'])
                    install_address = Address.objects.get(id = install_address_id)
                    ins = InstallationRequest(user = user, name = install_name, phone =install_phone, email = install_email, address = install_address)
                    ins.save()
            except:
                pass


            for item in items:
                print(item)
                item.order = order
                item.save()
                order.save()
                artist_earning = item.product.design.artist.artist.get_royalty_percent()*item.price/100
                artist = Artist.objects.get(user=item.product.design.artist)
                artist.earnings = artist.earnings + artist_earning
                artist.save()
                nt_ins2 = UserNotifications(user=item.product.design.artist, notification_type='design_purchase', text=f"{user.first_name} {user.last_name} Purchased {item.product.design.name}")
                nt_ins2.save()

            order_status = OrderStatus(order=order, name = 'pending')
            order_status.save()

            cart.is_ordered = True
            cart.save()
            serializer = OrderDetailSerializer(instance = order)

            return Response(data = serializer.data, status= status.HTTP_200_OK)

        else:
            return Response({'status': "Not verified"}, status=status.HTTP_400_BAD_REQUEST)
    
        # except Exception as e:
        #     return Response({'status': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ClientAddressView(APIView):

    permission_classes = [AllowAny]

    def get(self,request):
        client_pk = request.GET.get('client_id')
        client = ClientDetails.objects.get(pk=client_pk)
        address = client.address.all().order_by('pk').first()
        serializer = AddressSerializer(instance=address)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self,request):
        client_pk = request.data['client_id']
        print(client_pk)
        client = ClientDetails.objects.get(pk=client_pk)
        user = client.decorator
        ADDRESS_TYPE = [
                'Personal Address',
                'Business Address',
                'Shipping Address',
                'Billing Address',
                'Installation Address',
                'Client Address'
            ]
        personal_address = {
                'user': user.pk,
                'type': ADDRESS_TYPE.index('Client Address') +1,
                'line1': request.data['addressStreetAboutyouKey'],
                'line2': request.data['addressApartmentAboutyouKey'],
                'city': request.data['addressCityAboutyouKey'],
                'pincode': request.data['addressPincodeAboutyouKey'],
                'state': request.data['stateAboutyouKey']

            }
        peradd_serializer = AddressSerializer(
                            data=personal_address)
        if peradd_serializer.is_valid() :
            address = peradd_serializer.save()
            print(address)
            client.address.add(address)
            return Response(data=peradd_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({'error':peradd_serializer.errors},status=status.HTTP_400_BAD_REQUEST)

    def put(self,request):
        client_pk = request.data['client_id']
        print(client_pk)
        client = ClientDetails.objects.get(pk=client_pk)
        user = client.decorator
        ADDRESS_TYPE = [
                'Personal Address',
                'Business Address',
                'Shipping Address',
                'Billing Address',
                'Installation Address',
                'Client Address'
            ]
        personal_address = {
                'user': user.pk,
                'type': ADDRESS_TYPE.index('Client Address') +1,
                'line1': request.data['addressStreetAboutyouKey'],
                'line2': request.data['addressApartmentAboutyouKey'],
                'city': request.data['addressCityAboutyouKey'],
                'pincode': request.data['addressPincodeAboutyouKey'],
                'state': request.data['stateAboutyouKey']

            }
        addrs = Address.objects.get(pk=request.data['pk'])
        peradd_serializer = AddressSerializer(addrs,
                            data=personal_address)
        if peradd_serializer.is_valid() :
            address = peradd_serializer.save()
            print(address)
            return Response(data=peradd_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({'error':peradd_serializer.errors},status=status.HTTP_400_BAD_REQUEST)

## Firm Admin Order Views

class InitiateFirmOrder(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        amount = float(request.data['amount'])
        rp_pk = request.data['pk']
        item = PurchaseRequest.objects.get(pk=rp_pk)
        backend_price = item.price
        if int(backend_price) == int(amount):
            try:
                client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID,settings.RAZORPAY_KEY_SECRET))

                DATA = {
                    "amount": int(backend_price*100),
                    "currency": "INR",
                    "payment_capture":1
                    }
                    
                payment_order = client.order.create(data=DATA)                   
                                    
                return Response({
                    'status': "Success",
                    'amount':amount,
                    'api_key':settings.RAZORPAY_KEY_ID,
                    'order_id':payment_order['id'],
                    'payment_order_status':payment_order['status']
                    }, status=status.HTTP_200_OK)
            
            except Exception as e:
                return Response({'status': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'msg':"Price didn't match"}, status=status.HTTP_400_BAD_REQUEST)

class FirmPlaceOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # try:
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID,settings.RAZORPAY_KEY_SECRET))
        razorpay_order_id = request.data['razorpay_order_id']
        razorpay_payment_id = request.data['razorpay_payment_id']
        razorpay_signature = request.data['razorpay_signature']
        data = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }
        check = client.utility.verify_payment_signature(data)
        if check is None:
            rp_pk = request.data['pk']
            rp = PurchaseRequest.objects.get(pk = rp_pk)
            rp.is_approved = True
            rp.is_rejected = False
            rp.save()
            user = rp.decorator.user
            items = rp.items.all()
            amount = float(request.data['amount'])
            backend_price = rp.price
            try:
                shipping_address_id = int(request.data['shipping_address_id'])
                shipping_address = Address.objects.get(id = shipping_address_id)
            except:
                try:
                    shipping_address = Address.objects.filter(user = user)[0]
                except:
                    shipping_address = None

            try:
                billing_address_id = int(request.data['billing_address_id'])
                billing_address = Address.objects.get(id = billing_address_id)
            except:
                try:
                    billing_address = Address.objects.filter(user = user)[0]
                except:
                    billing_address = None

            order = Order(user = user, order_cost = backend_price , billing_address = billing_address,
                    shipping_address= shipping_address)
            order.save()
            admin_mail_sub = f"New order placed by {request.user.email}"
            message = f"A new order has been placed, details: https://thewallruscompany.com:8000/admin/orders/order/{order.id}/change/"
            send_admin_mail(admin_mail_sub,message)

            firm = Firm.objects.get(user__email = request.user.email)
            decorator = Interior_Decorator.objects.get(user = rp.decorator)
            reward = backend_price*(firm.get_commision_percent()/100)
            firm.reward_points = firm.reward_points + reward
            firm.save()

            ct_ins1 = CoinTransaction(user=request.user,description = f"For using in order(id:{order.pk}) ", amount=int(amount),credit=reward)
            ct_ins1.save()
            nt_ins = UserNotifications(user=user, notification_type='purchase-request', text=f"Firm Admin placed a order for {items.all().first().product.design.name}")
            nt_ins.save()
            nt_ins2 = UserNotifications(user=user, notification_type='purchase-request', text=f"Your purchase request accepted for {items.all().first().product.design.name}")
            nt_ins2.save()
            

            for item in items:
                print(item)
                item.order = order
                item.save()
                order.save()
                artist_earning = item.product.design.artist.artist.get_royalty_percent()*item.price/100
                artist = Artist.objects.get(user=item.product.design.artist)
                artist.earnings = artist.earnings + artist_earning
                artist.save()
                nt_ins2 = UserNotifications(user=item.product.design.artist, notification_type='design_purchase', text=f"{user.first_name} {user.last_name} Purchased {item.product.design.name}")
                nt_ins2.save()

            order_status = OrderStatus(order=order, name = 'pending')
            order_status.save()

            serializer = OrderDetailSerializer(instance = order)

            return Response(data = serializer.data, status= status.HTTP_200_OK)

        else:
            return Response({'status': "Not verified"}, status=status.HTTP_400_BAD_REQUEST)
    
        # except Exception as e:
        #     return Response({'status': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CancelOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        order_id = request.POST.get('order_id', None)

        if order_id:
            order = Order.objects.get(id=order_id)
            if order.user.id == request.user.id:
                old_status = OrderStatus.objects.filter(order=order).order_by('-timestamp')
                is_cancelled = old_status.filter(name = "cancelled").exists()
                if is_cancelled:
                    return Response({'msg':'This order is already cancelled'}, status=status.HTTP_400_BAD_REQUEST)
                if old_status.count() >0:
                    last_status = old_status[0]
                    if last_status.name != 'pending':
                        return Response({'msg':'the order is already confirmed, can\'t be cancelled now'}, status=status.HTTP_400_BAD_REQUEST)

                order_status = OrderStatus(order = order, name="cancelled")
                order_status.save()
                refund = Refund(order=order)
                refund.save()
                admin_mail_sub = f"Order cancelled by {request.user.email}"
                message = f"A order has been cancelled, refund details: https://thewallruscompany.com:8000/admin/orders/refund/{refund.id}/change/"
                send_admin_mail(admin_mail_sub,message)
                return Response({'msg':'success'}, status=status.HTTP_200_OK)
            return Response({'msg':"you are not authorised to cancell this order"}, status=status.HTTP_401_UNAUTHORIZED)
        return Response({'msg':'No order_id is given'}, status=status.HTTP_400_BAD_REQUEST)