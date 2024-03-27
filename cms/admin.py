from django.contrib import admin

# Register your models here.

from .models import Section, Content, AdminControl

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'header')
    def has_delete_permission(self, request, obj=None):
        # Disable delete
        return False

@admin.register(AdminControl)
class AdminControlAdmin(admin.ModelAdmin):
    list_display = ('name', 'value')

@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ('section', 'sequence_number', 'heading')
    search_fields = ('section__name', 'heading')
    list_filter = ('section', )
    def has_delete_permission(self, request, obj=None):
        # Disable delete
        return False