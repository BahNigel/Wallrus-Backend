from django.contrib import admin

from .models import Address, BusinessDetail, BankDetail, CoinTransaction
# Register your models here.

# admin.site.register(CoinTransaction)
@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'state', 'city', 'pincode')
    list_filter = ('type',)
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'user__username', 'user__phone')


class BusinessDetail(admin.StackedInline):
    model = BusinessDetail


class BankDetail(admin.StackedInline):
    model = BankDetail
