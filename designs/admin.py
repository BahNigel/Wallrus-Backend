from django.contrib import admin
from product.admin import *
from .models import Customization, DesignTag, Design, Colorway, UploadOwnDesign
# Register your models here.


class DesignTagAdmin(admin.ModelAdmin):
    list_display = ['name', 'label']
    search_fields = ['name', 'label']


admin.site.register(DesignTag, DesignTagAdmin)

class ColorwayAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'design')
    search_fields = ('design__name', 'design__id')
    list_filter = ('color_tags',)

admin.site.register(Colorway, ColorwayAdmin)

class Colorway(admin.TabularInline):
    model = Colorway


class DesignAdmin(admin.ModelAdmin):
    inlines = [Colorway, ProductAdminInline]
    list_display = ('id', 'artist', 'name', 'slug', 'created_at', 'is_customizable', 'is_approved', 'is_rejected')
    search_fields = ('slug', 'id', 'artist__phone', 'artist__email', 'artist__username', 'artist__first_name', 'name')
    list_filter = ('applications', 'tags', 'is_approved', 'is_rejected', 'is_customizable')
    class Meta:
        model = Design

admin.site.register(Design, DesignAdmin)

class CustomizationAdmin(admin.ModelAdmin):
    list_display = ('id' ,'name', 'phone_number', 'application', 'product' , 'remarks')
    list_filter = ('application',)
    search_fields = ('id' ,'name', 'phone_number', )

admin.site.register(Customization, CustomizationAdmin)

class UploadOwnDesignAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone_number', 'application', 'product' , 'remarks')
    list_filter = ('application',)
    search_fields = ('id' ,'name', 'phone_number', )

admin.site.register(UploadOwnDesign, UploadOwnDesignAdmin)
