"""
Rutas principales de la app Bar Galileo.
Define las URLs para vistas públicas, autenticación y CRUD de productos.
"""

from django.urls import path

app_name = "products"
from . import views
from . import views_api
from .views import ProductoDetailView

    #### rutas para el dashboard de las categorías
    path('adminD/categories/', views.CategoriasAdminView.as_view(), name='categories_admin'),
    path('adminD/categories/create/', views.CategoriaCreateAdminView.as_view(), name='categories_create_admin'),
    path('adminD/categories/update/<int:pk>/', views.CategoriaUpdateAdminView.as_view(), name='categories_edit_admin'),
    path('adminD/categories/delete/<int:pk>/', views.CategoriaDeleteAdminView.as_view(), name='categories_delete_admin'),
    #### rutas para el dashboard de los proveedores
    path('adminD/proveedores/', views.ProveedoresAdminView.as_view(), name='proveedores_admin'),
    path('adminD/proveedores/create/', views.ProveedorCreateAdminView.as_view(), name='proveedores_create_admin'),
    path('adminD/proveedores/update/<int:pk>/', views.ProveedorUpdateAdminView.as_view(), name='proveedores_edit_admin'),
    path('adminD/proveedores/delete/<int:pk>/', views.ProveedorDeleteAdminView.as_view(), name='proveedores_delete_admin'),

    #### rutas para el dashboard de brands (marcas)
    path('adminD/brands/', views.BrandsAdminView.as_view(), name='brands_admin'),
    path('adminD/brands/create/', views.BrandCreateAdminView.as_view(), name='brands_create_admin'),
    path('adminD/brands/update/<int:pk>/', views.BrandUpdateAdminView.as_view(), name='brands_update_admin'),
    path('adminD/brands/delete/<int:pk>/', views.BrandDeleteAdminView.as_view(), name='brands_delete_admin'),
<<<<<<< HEAD
    path('producto/<int:pk>/', ProductoDetailView.as_view(), name='producto_detalle'),
=======
>>>>>>> f550aac13c0202e2f4652738b7d329dd256a899a
]


