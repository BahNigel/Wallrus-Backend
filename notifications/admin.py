from django.contrib import admin

# Register your models here.
from .models import ArtistNotificationSettings, InteriorDecoratorNotificationSettings, NewsLetterSubscribers, UserNotifications


# admin.site.register(ArtistNotificationSettings)
# admin.site.register(DecoratorNotificationSetting)

class ArtistNotificationSettings(admin.StackedInline):
    model = ArtistNotificationSettings

class InteriorDecoratorNotificationSettings(admin.StackedInline):
    model = InteriorDecoratorNotificationSettings

class NewsLetterSubscribersAdmin(admin.ModelAdmin):
    list_display = ('email', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('email',)

admin.site.register(NewsLetterSubscribers, NewsLetterSubscribersAdmin)
# admin.site.register(UserNotifications)