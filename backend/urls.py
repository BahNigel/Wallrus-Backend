"""backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from . import settings
from django.contrib.auth.models import Group
from social_django.models import Association, Nonce, UserSocialAuth
from oauth2_provider.models import AccessToken, Application, Grant, IDToken, RefreshToken

try:
    admin.site.unregister(Association)
    admin.site.unregister(Nonce)
    admin.site.unregister(UserSocialAuth)
    admin.site.unregister(Group)
    admin.site.unregister(AccessToken)
    admin.site.unregister(Application)
    admin.site.unregister(Grant)
    admin.site.unregister(IDToken)
    admin.site.unregister(RefreshToken)
except:
    pass
admin.site.disable_action('delete_selected')
admin.site.site_header = 'Wallrus Adminstartion'
admin.site.site_title = 'Wallrus Site Adminstartion'
admin.site.index_title = 'Wallrus Admin'

urlpatterns = [
    # Oauth
    path('auth/', include('drf_social_oauth2.urls', namespace='drf')),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls'))
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
