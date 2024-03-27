from django.http.response import HttpResponse
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum
from datetime import datetime, timedelta

from users.models import CustomUser
from users.models import Interior_Decorator
from orders.models import Order, Item
from users.models import Artist
from product.models import Collection, Product

class BusinessAnalytic(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = datetime.now()
        
        custom_user = CustomUser.objects.get(email=request.user)
        # print(custom_user.designs.name)
        # print(custom_user.design_set.name)
        color = request.GET.get('color', None)
        theme = request.GET.get('theme', None)
        product = request.GET.get('sku', None)
        if request.user.type == 1:
            # print("I am artist...")
            items = Item.objects.filter(product__design__artist = request.user).exclude(order=None)
            total_orders = 0
            graphCoordinates = {}
            if color:
                items = items.filter(product__colorway__color_tags__name=color)
            if theme:
                items = items.filter(product__design__tags__name=theme)
            if product:
                items = items.filter(product__sku = product)
            for delta in range(7):
                date = today - timedelta(days=delta)
                num_of_orders = items.filter(order__created_at__gte=date).count() - total_orders 
                total_orders += num_of_orders
                graphCoordinates[date.strftime('%a')] = num_of_orders
            #############################################################

            # Counting the number of users following the requesting artist
            try:
                followers = Artist.objects.get(user=request.user).followers.count()
            except Exception as e:
                followers = f"{e}"

            # Counting numbers of favourate products of the requesting user 
            try:
                favourites = Product.objects.filter(favourited_by__email=request.user, favourited_by__is_active=True).count()
            except Exception as e:
                favourites = f"{e}"

            try:
                product_views = Product.objects.filter(design__artist = request.user).aggregate(Sum('views'))['views__sum']
            except Exception as e:
                product_views = e

            try:
                earnings = Artist.objects.get(user = request.user).earnings
            except Exception as e:
                earnings = e

            sales = Item.objects.filter(product__design__artist=request.user).exclude(order=None).exclude(order__order_status__name = 'pending').exclude(order__order_status__name = 'rejected').count()

            data = {}
            data['Graph Coordinates'] = graphCoordinates # Improve it
            data["Earning"] = float("{:.2f}".format(earnings))
            data["Sales"] = sales
            data["Followers"] = followers
            data["Favourites"] = favourites 
            data["Views"] = product_views
            return Response(data, status=status.HTTP_200_OK)

        elif request.user.type == 2:
            orders = Order.objects.filter(user= request.user)
            total_orders = 0
            graphCoordinates = {}
            for delta in range(7):
                date = today - timedelta(days=delta)
                num_of_orders = orders.filter(created_at__gte=date).count() - total_orders 
                total_orders += num_of_orders
                graphCoordinates[date.strftime('%a')] = num_of_orders
            
            # Counting numbers of the purchased orders
            purchased = Order.objects.filter(user= request.user, order_status__name="delivered").count()
            
            # Counting numbers of Artists followed by requesting decorator
            try:
                deco = Interior_Decorator.objects.get(user=request.user)
                following = Artist.objects.filter(followers=deco).count()
            except Exception as e:
                following = f"{e}"
            # try:
            #     no_of_followers_of_the_artist = Artist.objects.get(user=request.user).followers.count()
            # except Exception as e:
            #     no_of_followers_of_the_artist = f"{e}"

            # Counting numbers of collections of the user
            try:
                collections = Collection.objects.filter(user=request.user.id).count()
            except Exception as e:
                collections = f"{e}"

            # Counting numbers of favourate products of the requesting user 
            try:
                favourites = Product.objects.filter(favourited_by__email=request.user, favourited_by__is_active=True).count()
            except Exception as e:
                favourites = f"{e}"

            try:
                coins = Interior_Decorator.objects.get(user=request.user).coins
            except Exception as e:
                coins = e

            data = {}
            data['Graph Coordinates'] = graphCoordinates
            data['Purchased'] = purchased
            data['Following'] = following
            data['Favourites'] = favourites
            data['Collection'] = collections
            data['Wallrus Coins'] = coins
            return Response(data, status=status.HTTP_200_OK)
        else:
            data = {}
            data["details"] = "The requesting user is not allowed."
            return Response(data, status=status.HTTP_401_UNAUTHORIZED)

class PlatinumArtistBusinessAnalytic(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = datetime.now()
        
        custom_user = CustomUser.objects.get(email=request.user)
        # print(custom_user.designs.name)
        # print(custom_user.design_set.name)
        color = request.GET.get('color', None)
        theme = request.GET.get('theme', None)
        product = request.GET.get('sku', None)
        if request.user.type == 1:
            # print("I am artist...")
            artist = Artist.objects.get(user=request.user)
            if artist.level.name == 4:
                items = Item.objects.all().exclude(order=None)
                total_orders = 0
                graphCoordinates = {}
                if color:
                    items = items.filter(product__colorway__color_tags__name=color)
                if theme:
                    items = items.filter(product__design__tags__name=theme)
                if product:
                    items = items.filter(product__sku = product)
                for delta in range(7):
                    date = today - timedelta(days=delta)
                    num_of_orders = items.filter(order__created_at__gte=date).count() - total_orders 
                    total_orders += num_of_orders
                    graphCoordinates[date.strftime('%a')] = num_of_orders
                #############################################################

                data = {}
                data['Graph Coordinates'] = graphCoordinates # Improve it
                
                return Response(data, status=status.HTTP_200_OK)
            return Response({'msg':'User is not a platinum user'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'msg':'User is not a Artist'}, status=status.HTTP_400_BAD_REQUEST)