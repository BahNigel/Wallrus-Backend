from django.contrib import admin
from .models import *
from designs.models import *
from django_admin_inline_paginator.admin import TabularInlinePaginated
# Register your models here.

class ProductAdminInline(TabularInlinePaginated):
    per_page = 1
    model = Product

class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('name', 'pricing_category', 'is_active')
    list_filter = ('pricing_category', 'is_active')

admin.site.register(Application, ApplicationAdmin)

class MaterialAdmin(admin.ModelAdmin):
    list_display = ('name', 'application', 'is_active')
    list_filter = ('application', 'is_active')

admin.site.register(Material, MaterialAdmin)

class ProductImageAdmin(admin.StackedInline):
    model = ProductImages


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    fields = ('application', 'design', 'colorway', 'views', 'is_active', 'slug', 'slug_tag')
    list_display = ('sku', 'application', 'design', 'colorway', 'views', 'is_active', 'slug', 'slug_tag')
    list_filter = ('is_active', 'application')
    search_fields = ('sku', 'design__name', 'design__artist__email', 'design__artist__phone', 'design__artist__username', 'design__artist__first_name')
    inlines = [ProductImageAdmin]
    raw_id_fields = ['design', 'colorway']
    def get_form(self, request, obj=None, **kwargs):
        self.exclude = ('favourited_by')
        form = super(ProductAdmin, self).get_form(request, obj, **kwargs)
        # form.base_fields['design'].queryset = Design.objects.filter(is_approved = True).order_by('-created_at')[0:10]
        # form.base_fields['colorway'].queryset = Colorway.objects.all()[0:2]
        # form.base_fields['favourited_by'].queryset = CustomUser.objects.filter(is_active = True)[0:10]
        return form

    class Media:
        js = ("js/admin_product.js",)

# admin.site.register(Tag)

# admin.site.register(Reviews)
# admin.site.register(Collection)
# admin.site.register(CollectionTag)
# admin.site.register(Coupon)