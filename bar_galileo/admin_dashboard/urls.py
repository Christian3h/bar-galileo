from django.urls import path
from .views import (
    DashboardView, export_dashboard,
    ImageManagementView,
    CarouselImageCreateView, CarouselImageUpdateView, CarouselImageDeleteView,
    carousel_reorder_ajax, carousel_toggle_active,
    SiteImageSectionCreateView, SiteImageSectionUpdateView,
    SiteImageCreateView, SiteImageUpdateView, SiteImageDeleteView,
    site_image_toggle_active
)

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('export/<str:fmt>/', export_dashboard, name='export_dashboard'),
    
    # Gestión de imágenes
    path('images/', ImageManagementView.as_view(), name='image_management'),
    
    # Carrusel
    path('images/carousel/create/', CarouselImageCreateView.as_view(), name='carousel_image_create'),
    path('images/carousel/<int:pk>/edit/', CarouselImageUpdateView.as_view(), name='carousel_image_edit'),
    path('images/carousel/<int:pk>/delete/', CarouselImageDeleteView.as_view(), name='carousel_image_delete'),
    path('images/carousel/reorder/', carousel_reorder_ajax, name='carousel_reorder'),
    path('images/carousel/<int:pk>/toggle/', carousel_toggle_active, name='carousel_toggle_active'),
    
    # Secciones
    path('images/sections/create/', SiteImageSectionCreateView.as_view(), name='site_image_section_create'),
    path('images/sections/<int:pk>/edit/', SiteImageSectionUpdateView.as_view(), name='site_image_section_edit'),
    
    # Imágenes del sitio
    path('images/site/create/', SiteImageCreateView.as_view(), name='site_image_create'),
    path('images/site/<int:pk>/edit/', SiteImageUpdateView.as_view(), name='site_image_edit'),
    path('images/site/<int:pk>/delete/', SiteImageDeleteView.as_view(), name='site_image_delete'),
    path('images/site/<int:pk>/toggle/', site_image_toggle_active, name='site_image_toggle_active'),
]