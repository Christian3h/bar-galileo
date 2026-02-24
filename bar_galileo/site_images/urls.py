from django.urls import path
from .views import (
    ImageManagementView,
    CarouselImageCreateView, CarouselImageUpdateView, CarouselImageDeleteView,
    carousel_reorder_ajax, carousel_toggle_active,
    SiteImageSectionCreateView, SiteImageSectionUpdateView,
    SiteImageCreateView, SiteImageUpdateView, SiteImageDeleteView,
    site_image_toggle_active,
    SiteContentListView, SiteContentEditView,
)

app_name = 'site_images'

urlpatterns = [
    # Vista principal
    path('', ImageManagementView.as_view(), name='image_management'),

    # Carrusel
    path('carousel/create/', CarouselImageCreateView.as_view(), name='carousel_image_create'),
    path('carousel/<int:pk>/edit/', CarouselImageUpdateView.as_view(), name='carousel_image_edit'),
    path('carousel/<int:pk>/delete/', CarouselImageDeleteView.as_view(), name='carousel_image_delete'),
    path('carousel/reorder/', carousel_reorder_ajax, name='carousel_reorder'),
    path('carousel/<int:pk>/toggle/', carousel_toggle_active, name='carousel_toggle_active'),

    # Secciones
    path('sections/create/', SiteImageSectionCreateView.as_view(), name='site_image_section_create'),
    path('sections/<int:pk>/edit/', SiteImageSectionUpdateView.as_view(), name='site_image_section_edit'),

    # Imágenes del sitio
    path('site/create/', SiteImageCreateView.as_view(), name='site_image_create'),
    path('site/<int:pk>/edit/', SiteImageUpdateView.as_view(), name='site_image_edit'),
    path('site/<int:pk>/delete/', SiteImageDeleteView.as_view(), name='site_image_delete'),
    path('site/<int:pk>/toggle/', site_image_toggle_active, name='site_image_toggle_active'),

    # Contenido de la home
    path('content/', SiteContentListView.as_view(), name='site_content_list'),
    path('content/<str:section>/edit/', SiteContentEditView.as_view(), name='site_content_edit'),
]
