"""manager URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from manager import settings
from carbina.api import views as api_views

router = routers.DefaultRouter()
router.register(r'clients', api_views.ClientList)
router.register(r'client-detail', api_views.ClientDetail)

urlpatterns = [
    path('', include('dashboard.urls')),
    path('admin/', admin.site.urls),
    path('accounts/', include('employee_auth.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('carbina/', include('carbina.urls')),
    path('django-rq/', include('django_rq.urls')),
    path('api/', include(router.urls)),
    path('api/carbina/clients/', api_views.ClientList.as_view({'get': 'list'}), name="client-list-api"),
    path('api/carbina/clients/<int:pk>/detail/', api_views.ClientDetail.as_view({'get': 'retrieve'}), name="client-detail"),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = 'Arena Tree Specialists Admin'
admin.site.index_title = 'Home // Arena Tree Specialists Administration'
admin.site.site_title = 'Arena Tree Specialists Administration'