from django.contrib import admin
from django.contrib.admin.options import ModelAdmin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _

from .models import *
# Register your models here.
from user_details.admin import BankDetail, BusinessDetail
from notifications.admin import ArtistNotificationSettings, InteriorDecoratorNotificationSettings


class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Information'), {
            'fields': ('profile_picture', 'first_name', 'last_name', 'phone', 'username', 'type', 'bio', 'Unique_id')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff',
                                       'is_superuser', 'groups', 'user_permissions')}),
        (_('Login Details'), {'fields': ('date_joined', 'last_login')})
    )
    inlines = [BusinessDetail, BankDetail]
    add_fieldsets = (
        (None, {
            'classes': ('wide', ),
            'fields': ('email', 'password1', 'password2', 'type')
        }),
    )

    list_display = ('id', 'email', 'phone', 'first_name',
                    'last_name', 'type', 'is_active')
    search_fields = ('email', 'phone')
    ordering = ['-id',]


admin.site.register(CustomUser, CustomUserAdmin)
# admin.site.register(RandomPassword)
# admin.site.register(Code)
# admin.site.register(Interior_Decorator)
# admin.site.register(OtpTable)


@admin.register(Artist)
class ArtistAdmin(ModelAdmin):
    inlines = [ArtistNotificationSettings]
    list_display = ('user', 'level', 'earnings')
    search_fields = ('user__email', 'user__phone', 'user__username', 'user__first_name')
    list_filter = ('level',)

@admin.register(Interior_Decorator)
class InteriorDecoratorAdmin(ModelAdmin):
    inlines = [InteriorDecoratorNotificationSettings]
    list_display = ('user', 'level', 'reward_points')
    search_fields = ('user__email', 'user__phone', 'user__username', 'user__first_name')
    list_filter = ('level',)


class FirmAdmin(admin.ModelAdmin):
    list_display = ('user', 'level', 'platinum_commission_percent')
    search_fields = ('user__email', 'user__phone', 'user__username', 'user__first_name')
    list_filter = ('level',)

admin.site.register(Firm, FirmAdmin)