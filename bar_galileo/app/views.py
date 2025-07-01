<<<<<<< HEAD
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .models import Categoria, Producto  # ajusta según tus modelos
from django.contrib.auth.models import User
from django.contrib import messages

# vistas públicas

def index(request):
    return render(request, "public/index.html")

def nosotros(request):
    return render(request, "public/nosotros.html")

def menu(request):
    categorias = Categoria.objects.all()
    productos = Producto.objects.select_related("id_categoria")
    ctx = {"categorias": categorias, "productos": productos}
    return render(request, "public/menu.html", ctx)

# reservas

def reserva_eventos(request):
    return render(request, "public/reservas/eventos.html")

def reserva_grupal(request):
    return render(request, "public/reservas/grupal.html")

# autenticación básica

def login_view(request):
    if request.method == "POST":
        user = authenticate(request, username=request.POST["username"], password=request.POST["password"])
        if user is not None:
            login(request, user)
            return redirect("index")
    return render(request, "auth/login.html")

def logout_view(request):
    logout(request)
    return redirect("index")


def signup_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        if User.objects.filter(username=username).exists():
            messages.error(request, "El usuario ya existe")
        else:
            User.objects.create_user(username=username, password=password)
            messages.success(request, "Cuenta creada. Inicia sesión.")
            return redirect("login")
    return render(request, "auth/signup.html")
=======
from django.shortcuts import render

# Create your views here.
>>>>>>> 1c874fa6395b9a3ad88fc257072f9c1a4052f229
