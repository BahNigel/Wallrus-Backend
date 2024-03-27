from django.contrib import admin
from django.contrib.admin.options import ModelAdmin
from django_admin_inline_paginator.admin import TabularInlinePaginated

# Register your models here.
from .models import *

# admin.site.register(Cart)
# admin.site.register(PurchaseRequest)
# admin.site.register(ClientDetails)
# admin.site.register(ClientCart)
class OrderStatus(admin.StackedInline):
    model = OrderStatus

class ItemAdminInline(TabularInlinePaginated):
    fieldsets = [( None, {'fields':('material', 'product', 'quantity', 'width', 'height', 'unit')})]
    per_page = 10
    model = Item

@admin.register(Order)
class OrderAdmin(ModelAdmin):
    inlines = [OrderStatus, ItemAdminInline]
    list_display = ('user', 'order_cost','created_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'user__username', 'user__phone')
    list_filter = ('created_at',)

    def get_form(self, request, obj, **kwargs):
        form = super(OrderAdmin, self).get_form(request, obj, **kwargs)
        # form.base_fields['items'].queryset = obj.items.all()
        return form

    def has_add_permission(self, request, obj=None):
        return False

@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ('user','order', 'amount_refunded', 'created_at','is_refunded', 'transaction_id')
    search_fields = ('order__user__email', 'order__user__first_name', 'order__user__last_name', 'order__user__username', 'order__user__phone')
    list_filter = ('is_refunded','created_at')
    def user(self, obj):
        if obj.order.user:
            return obj.order.user
        return None
    user.short_description = 'User'
    user.admin_order_field = 'order__user'

    def has_add_permission(self, request, obj=None):
        return False

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'quantity', 'width', 'height', 'unit', 'material', 'price')
    search_fields = ('id',)

@admin.register(MeasurementRequest)
class MeasurementRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'state', 'city', 'pincode', 'date', 'timeframe_of_measurement', 'is_approved')
    search_fields = ('name', 'id')
    list_filter = ('is_approved','state', 'city', 'date')