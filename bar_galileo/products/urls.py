"""
Rutas principales de la app Bar Galileo.
Define las URLs para vistas públicas, autenticación y CRUD de productos.
"""

from django.urls import path
from . import views
from . import views_api  
from .views import EliminarImagenProductoView


urlpatterns = [
    # path("", views.IndexView.as_view(), name="index"),  # Página principal
    # path("nosotros/", views.NosotrosView.as_view(), name="nosotros"),  # Página 'Nosotros'
    # path("menu/", views.MenuView.as_view(), name="menu"),  # Menú de productos
    # path("reservas/eventos/", views.ReservaEventosView.as_view(), name="reserva_eventos"),  # Reservas de eventos
    # path("reservas/grupal/", views.ReservaGrupalView.as_view(), name="reserva_grupal"),  # Reservas grupales
    # path("login/", views.LoginView.as_view(), name="login"),  # Login de usuario
    # path("logout/", views.LogoutView.as_view(), name="logout"),  # Logout de usuario
    # path("signup/", views.SignupView.as_view(), name="signup"),  # Registro de usuario
    path('api/productos/', views.ProductosJsonView.as_view(), name='productos_json'),  # API productos (JSON)
    path('api/proveedores/', views_api.proveedores_json, name='proveedores_json'),  # API proveedores (JSON)
    path('api/marcas/', views_api.marcas_json, name='marcas_json'),  # API marcas (JSON)
    path('api/categorias/', views_api.categorias_json, name='categorias_json'),  # API categorías (JSON)
    path("productos/", views.ProductosView.as_view(), name="productos"),  # Listado y alta de productos
    path("productos/editar/<int:pk>/", views.ProductoUpdateView.as_view(), name="producto_editar"),  # Editar producto
    path("productos/eliminar/<int:pk>/", views.ProductoDeleteView.as_view(), name="producto_eliminar"),  # Eliminar producto
    path("categorias/", views.CategoriasView.as_view(), name="categorias"),  # Listado y alta de categorías
    path("categorias/editar/<int:pk>/", views.CategoriaUpdateView.as_view(), name="categoria_editar"),  # Editar categoría
    path("categorias/eliminar/<int:pk>/", views.CategoriaDeleteView.as_view(), name="categoria_eliminar"),  # Eliminar categoría
    path("proveedores/", views.ProveedoresView.as_view(), name="proveedores"),  # Listado y alta de proveedores
    path("proveedores/editar/<int:pk>/", views.ProveedorUpdateView.as_view(), name="proveedor_editar"),  # Editar proveedor
    path("proveedores/eliminar/<int:pk>/", views.ProveedorDeleteView.as_view(), name="proveedor_eliminar"),  # Eliminar proveedor
    path("marcas/", views.MarcasView.as_view(), name="marcas"),  # Listado y alta de marcas
    path("marcas/editar/<int:pk>/", views.MarcaUpdateView.as_view(), name="marca_editar"),  # Editar marca
    path("marcas/eliminar/<int:pk>/", views.MarcaDeleteView.as_view(), name="marca_eliminar"),  # Eliminar marca
    path("productos/imagen/eliminar/<int:pk>/", EliminarImagenProductoView.as_view(), name="producto_imagen_eliminar"),
    # URLs para gestión de stock
    path("stock/", views.StockView.as_view(), name="stock"),  # Vista principal de stock
    path("stock/actualizar/", views.actualizar_stock, name="actualizar_stock"),  # Actualizar stock
    path('api/stock/', views.StockJsonView.as_view(), name='stock_json'),  # API stock (JSON)

]


