from django.contrib import admin
from .models import RoyaltyGroup, CommissionGroup
# Register your models here.

class RoyaltyGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'royalty_percent', 'min_design', 'min_revenue')

admin.site.register(RoyaltyGroup, RoyaltyGroupAdmin)

class CommissionGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'commission_percent', 'min_order', 'min_revenue')

admin.site.register(CommissionGroup, CommissionGroupAdmin)
