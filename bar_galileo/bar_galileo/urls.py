<<<<<<< HEAD
from django.urls import path
from app import views

urlpatterns = [
    path("", views.index, name="index"),
    path("nosotros/", views.nosotros, name="nosotros"),
    path("menu/", views.menu, name="menu"),
    path("reservas/eventos/", views.reserva_eventos, name="reserva_eventos"),
    path("reservas/grupal/", views.reserva_grupal, name="reserva_grupal"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("signup/", views.signup_view, name="signup"),
]


# from django.urls import path, include
# from . import views

# urlpatterns = [
#     # Público
#     path("", views.index, name="index"),
#     path("menu/", views.menu, name="menu"),

#     # Reservas
#     path("reservas/eventos/", views.reserva_eventos, name="reserva_eventos"),
#     path("reservas/grupal/", views.reserva_grupal, name="reserva_grupal"),

#     # Auth
#     path("login/", views.login_view, name="login"),
#     path("logout/", views.logout_view, name="logout"),
#     path("signup/", views.signup_view, name="signup"),

#     # Sub‑apps para back‑office
#     path("oper/", include("app.urls_oper")),
#     path("inv/", include("app.urls_inv")),
#     path("fin/", include("app.urls_fin")),
    
# ]
=======
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
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
]
>>>>>>> 1c874fa6395b9a3ad88fc257072f9c1a4052f229
