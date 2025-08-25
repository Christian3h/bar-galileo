"""
URL configuration for bar_galileo project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', include(('products.urls', 'products'), namespace='products')),
    path('', include(('core.urls', 'core'), namespace='core')),
    path('', include(('tables.urls', 'tables'), namespace='tables')),
    path('dashboard/', include(('admin_dashboard.urls', 'admin_dashboard'), namespace='admin_dashboard')),
    path('rol/', include(('roles.urls', 'roles'), namespace='roles')),
    path('facturacion/', include(('facturacion.urls', 'facturacion'), namespace='facturacion')),
    path('', include(('users.urls', 'users'), namespace='users')),
    path('', include(('notifications.urls', 'notifications'), namespace='notifications')),
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)