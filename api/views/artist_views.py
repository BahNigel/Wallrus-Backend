from datetime import date
from django.shortcuts import get_object_or_404
from rest_framework.serializers import Serializer

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.authentication import BasicAuthentication
from users.models import CustomUser, Artist, Interior_Decorator
from designs.models import DesignTag, Design
from django.contrib.auth import update_session_auth_hash
from ..serializers import *
from django.db.models import Count
import json
from api.custom_pagination import CustomPageNumberPagination

from ..utils import send_admin_mail


class ArtistSnippet(APIView):
    '''
    Fetch Details for Artist Snippet
    '''
    permission_classes = [IsAuthenticated]

    def get_object(self, user):
        return get_object_or_404(CustomUser, is_active=True, type=1, email=user)

    def get(self, request):
        user = self.get_object(request.user)
        serializer = ArtistSnippetSerializer(instance=user)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class ArtistDesign(APIView):
    '''
    Fetch Artist Designs
    '''
    permission_classes = [IsAuthenticated]
    def get_object(self, id):
        return get_object_or_404(CustomUser, type=1, Unique_id = id)

    def get(self, request,id):
        user = self.get_object(id)
        color = request.GET.get('color', None)
        theme = request.GET.get('theme', None)
        product = request.GET.get('sku', None)
        design_name = request.GET.get('design_name', None)
        sort = request.GET.get('sort_by', None)
        products = Product.objects.filter(design__artist = user)
        if color:
            products = products.filter(colorway__color_tags__name=color)
        if theme:
            products = products.filter(design__tags__name=theme)
        if product:
            products = products.filter(sku = product)
        if design_name:
            products = products.filter(design__name=design_name)

        if sort and sort == 'revenue':
            products =  sorted(products, key = lambda p: p.get_total_revenue(), reverse=True)
        elif sort and sort == 'view':
            products = products.filter(design__artist = user).order_by('-views')
        elif sort and sort == 'sales':
            products =  sorted(products, key = lambda p: p.get_total_sale() , reverse=True)
        else:
            products = products.filter(design__artist = user).order_by('-created_at')
            
        context = {'request': request}
        paginator = CustomPageNumberPagination()
        result_page = paginator.paginate_queryset(products,request)
        serializer = ArtistDesignSerializer(instance=result_page, many=True, context=context)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class DesignTagList(APIView):
    '''
    Tags list by label for upload design form
    '''

    def get(self, request):
        # back to original
        list = DesignTag.objects.values('label').distinct()
        serializer = DesignTagSerializer(instance=list, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class UploadDesign(APIView):
    '''
    To save a design in the database
    '''

    permission_classes = [IsAuthenticated]

    def get_user_obj(self, user_email):
        return get_object_or_404(CustomUser, type=1, email=user_email)

    def post(self, request):
        data = request.data
        print(data)
        for tag in data['tagDesignStyle']:
            style_tag = DesignTag.objects.filter(name=tag)
            if not style_tag.exists():
                DesignTag.objects.create(name=tag, label='Style')

        for tag in data['tagTheme']:
            style_tag = DesignTag.objects.filter(name=tag)
            if not style_tag.exists():
                DesignTag.objects.create(name=tag, label='Theme')

        style_tags = [{'label': 'Style',
                       'name': tag} for tag in data['tagDesignStyle']]

        theme_tags = [{'label': 'Theme',
                       'name': tag} for tag in data['tagTheme']]

        design_data = {
            'artist': request.user.id,
            'name': data['designName'],
            'is_customizable': True if data['customizable'] == 'Yes' else False,
            'applications': [{'name': app} for app in data['selectApp'] if app],
            'tags': style_tags + theme_tags
        }

        design_serializer = UploadDesignSerializer(data=design_data)
        if design_serializer.is_valid():
            print("1------------------------------")
            design = design_serializer.save()
            admin_mail_sub = f"New Design Uploaded by {request.user.email}"
            message = f"A new design has been uploaded, to approve follow to following url https://thewallruscompany.com:8000/admin/designs/design/{design.id}/change/"
            send_admin_mail(admin_mail_sub,message)
            if design:
                print("2-----------------------")
                design_ins = Design.objects.get(pk=design.pk)
                for tag in design_data['tags']:
                    try:
                        t = DesignTag.objects.get(name=tag['name'])
                        design_ins.tags.add(t)
                    except:
                        pass

                # adding new color tags if any
                color_tags = list(set([tag for colorway in data['colorwayArray']
                                       for tag in colorway['tagColor']]))
                for tag in color_tags:
                    tag_obj = DesignTag.objects.filter(name=tag)
                    if not tag_obj.exists():
                        DesignTag.objects.create(name=tag, label='Color')

                # adding colorways
                def modify_link(link):
                    try:
                        s_link = link.split('/file/d/')
                        if s_link[0].split('/')[-1] == "drive.google.com":
                            img_id = s_link[1].split('/')[0]
                            final_link = "https://drive.google.com/uc?export=view&id=" + img_id
                        else:
                            final_link = link
                        return final_link
                    except:
                        return link
                colorway_data = [{'design': design.pk,
                                  'name': colorway['name'],
                                  'image_url': modify_link(colorway['link']),
                                  'color_tags': [{'label': 'Color',
                                                  'name': tag} for tag in colorway['tagColor']]

                                  }
                                 for colorway in data['colorwayArray']]

                colorway_serializer = ColowaySerializer(
                    data=colorway_data, many=True)
                if colorway_serializer.is_valid():
                    colorways = colorway_serializer.save()
                    for colorway in colorways:
                        colorway = Colorway.objects.get(pk=colorway.pk)
                        for tag in color_tags:
                            try:
                                tag_obj = DesignTag.objects.get(name=tag)
                                colorway.color_tags.add(tag_obj)
                            except:
                                pass

                else:
                    return Response(data=colorway_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            else:
                print("3-------------------")
                print(design_serializer.errors)
                return Response(data=design_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response(data='Design has been uploaded', status=status.HTTP_201_CREATED)
        else:
            print(design_serializer.errors)
            return Response(data=design_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UnderReviewView(APIView):
    '''
    List of Design with is_approved=False
    '''
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # back to originalpath('user-type/', views.UserTypeView.as_view(), name='user-type'),
        list = Design.objects.filter(artist = request.user, is_approved=False, is_rejected=False).order_by('-created_at')
        paginator = CustomPageNumberPagination()
        result_page = paginator.paginate_queryset(list,request)
        serializer = UnderReviewSerializer(instance=result_page, many=True)
        # return paginator.get_paginated_response(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class FeaturedArtistListView(APIView):
    '''
    Featured Artist List Based on Followers
    '''
    def get(self, request):
        # back to original
        user_list = Artist.objects.all().annotate(count_follower=Count('followers')).order_by('-count_follower')[:5]
        serializer = FeaturedArtistListSerializer(instance=user_list, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

class ArtistListStatus(APIView):
    '''
    Artist List with status
    '''

    # authentication_classes=[BasicAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]


    def get(self,request):
        sort = request.GET.get('sort-by', None)
        if sort is not None:
            if sort == 'new':
                user_list = Artist.objects.all().order_by('-user__date_joined')
            elif sort == "recommended":
                user_list = Artist.objects.all().annotate(count_follower=Count('followers')).order_by('-count_follower','-user__date_joined')
            elif sort == "most-followed":
                user_list = Artist.objects.all().annotate(count_follower=Count('followers')).order_by('-count_follower')
            else:
                user_list = Artist.objects.all().annotate(count_follower=Count('followers')).order_by('-count_follower')
        else:
            user_list = Artist.objects.all().annotate(count_follower=Count('followers')).order_by('-count_follower','-user__date_joined')
        context = {'request': request} 
        paginator = CustomPageNumberPagination()
        result_page = paginator.paginate_queryset(user_list,request)
        serializer = ArtistListStatusSerializer(instance=result_page,context=context, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    
    def post(self,request):        
        Art = Artist.objects.get(user__Unique_id=request.data['id'])
        Int_Dec = Interior_Decorator.objects.get(user = request.user.id)
        cond = Artist.objects.filter(user__Unique_id=request.data['id'], followers=Int_Dec).exists()
        print(cond)
        if cond:
            Art.followers.remove(Int_Dec)
            Art.save()
            return Response(data='Artist Removed', status=status.HTTP_200_OK)
        else:
            Art.followers.add(Int_Dec)
            Art.save()   
            return Response(data='Artist Added', status=status.HTTP_200_OK)

class ArtistDetails(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request,id):
        artist = Artist.objects.get(user__Unique_id = id)
        context = {'request': request}
        serializer = ArtistDetailsSerializer(instance=artist, context=context)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class DeleteDesign(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self,request):
        user = request.user
        sku = request.data['sku']
        product = Product.objects.get(sku =sku)
        design = product.design
        if design.artist.email == user.email :
            design.delete()
            return Response({'msg':'deleted'}, status=status.HTTP_200_OK)
        else:
            return Response({'msg':'You don\'t have the permission to delete'}, status=status.HTTP_400_BAD_REQUEST)


