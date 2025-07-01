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