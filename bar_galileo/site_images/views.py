from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from roles.decorators import permission_required
import json

from django.shortcuts import redirect
from .models import SiteImage, CarouselImage, SiteImageSection, SiteContent
from .forms import SiteImageForm, CarouselImageForm, SiteImageSectionForm, SiteContentForm

SECTIONS_DEFAULT = {
    'hero': {
        'hero_title': 'BAR GALILEO',
        'hero_subtitle': 'Donde cada cerveza cuenta una historia y cada noche se convierte en una experiencia inolvidable.',
        'hero_button1_text': 'EXPLORAR CARTA',
        'hero_button2_text': 'NUESTRA HISTORIA',
    },
    'about': {
        'about_title': 'Acerca de Bar Galileo',
        'about_paragraph1': 'Somos más que un bar, somos un espacio donde la pasión por la coctelería se encuentra con la elegancia y el diseño. Nuestro equipo de mixólogos expertos crea experiencias únicas para cada huésped.',
        'about_paragraph2': 'Con una carta cuidadosamente seleccionada de destilados premium, ingredientes frescos y técnicas innovadoras, transformamos cada cóctel en una experiencia sensorial inolvidable.',
        'about_paragraph3': 'Únete a nosotros y descubre por qué Bar Galileo se ha convertido en el destino preferido para los amantes de la buena coctelería en la ciudad.',
    },
    'cocktails': {
        'cocktails_title': 'CÓCTELES',
        'cocktails_subtitle': 'Creaciones únicas de nuestros mixólogos expertos, elaboradas con los mejores ingredientes del mundo.',
    },
    'services': {
        'services_title': '¿Qué hace especial a BAR GALILEO?',
        'services_subtitle': 'Ofrecemos una experiencia integral de coctelería premium con atención personalizada en cada detalle.',
        'service1_number': '5+', 'service1_title': 'Años de experiencia', 'service1_description': 'Perfeccionando el arte de la mixología y creando momentos únicos.',
        'service2_number': '150+', 'service2_title': 'Cócteles únicos', 'service2_description': 'Carta exclusiva con creaciones propias y clásicos reimaginados.',
        'service3_number': '24/7', 'service3_title': 'Reservaciones', 'service3_description': 'Sistema de reservas disponible las 24 horas para tu comodidad.',
        'service4_number': '100%', 'service4_title': 'Satisfacción', 'service4_description': 'Compromiso total con la excelencia en cada experiencia.',
    },
    'reservations': {
        'reservations_title': 'Reservas',
        'reservations_text': '¡Reserva tu mesa y asegura tu lugar en Bar Galileo!',
        'reservations_whatsapp': '573044029343',
        'reservations_button_text': 'Reservar por WhatsApp',
    },
}


# ==================== VISTA PRINCIPAL ====================

@method_decorator([permission_required('dashboard', 'editar'), ensure_csrf_cookie], name='dispatch')
class ImageManagementView(TemplateView):
    """Vista principal de gestión de imágenes"""
    template_name = 'site_images/image_management.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['carousel_images'] = CarouselImage.objects.all().order_by('order')

        # Todas las secciones con sus imágenes
        sections = SiteImageSection.objects.prefetch_related('images').order_by('section_type', 'name')
        context['all_sections'] = sections

        # Imágenes agrupadas por sección
        context['about_images'] = SiteImage.objects.select_related('section').filter(section__section_type='about')
        return context


# ==================== CARRUSEL ====================

@method_decorator(permission_required('dashboard', 'crear'), name='dispatch')
class CarouselImageCreateView(CreateView):
    """Vista para crear una nueva imagen del carrusel"""
    model = CarouselImage
    form_class = CarouselImageForm
    template_name = 'site_images/carousel_image_form.html'
    success_url = reverse_lazy('site_images:image_management')

    def form_valid(self, form):
        messages.success(self.request, '¡Imagen del carrusel agregada exitosamente!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Error al agregar la imagen. Por favor, verifica los datos.')
        return super().form_invalid(form)


@method_decorator(permission_required('dashboard', 'editar'), name='dispatch')
class CarouselImageUpdateView(UpdateView):
    """Vista para editar una imagen del carrusel"""
    model = CarouselImage
    form_class = CarouselImageForm
    template_name = 'site_images/carousel_image_form.html'
    success_url = reverse_lazy('site_images:image_management')
    pk_url_kwarg = 'pk'

    def form_valid(self, form):
        messages.success(self.request, '¡Imagen del carrusel actualizada exitosamente!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Error al actualizar la imagen. Por favor, verifica los datos.')
        return super().form_invalid(form)


@method_decorator(permission_required('dashboard', 'eliminar'), name='dispatch')
class CarouselImageDeleteView(DeleteView):
    """Vista para eliminar una imagen del carrusel"""
    model = CarouselImage
    success_url = reverse_lazy('site_images:image_management')
    pk_url_kwarg = 'pk'

    def delete(self, request, *args, **kwargs):
        messages.success(request, '¡Imagen del carrusel eliminada exitosamente!')
        return super().delete(request, *args, **kwargs)


@require_POST
@permission_required('dashboard', 'editar')
def carousel_reorder_ajax(request):
    """Vista AJAX para reordenar imágenes del carrusel"""
    try:
        data = json.loads(request.body)
        image_orders = data.get('image_orders', [])

        for item in image_orders:
            image_id = item.get('id')
            new_order = item.get('order')

            if image_id and new_order is not None:
                CarouselImage.objects.filter(id=image_id).update(order=new_order)

        return JsonResponse({'success': True, 'message': 'Orden actualizado correctamente'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


@require_POST
@permission_required('dashboard', 'editar')
def carousel_toggle_active(request, pk):
    """Vista AJAX para activar/desactivar una imagen del carrusel"""
    try:
        image = get_object_or_404(CarouselImage, pk=pk)
        image.is_active = not image.is_active
        image.save()

        return JsonResponse({
            'success': True,
            'is_active': image.is_active,
            'message': 'Estado actualizado correctamente'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


# ==================== SECCIONES ====================

@method_decorator(permission_required('dashboard', 'crear'), name='dispatch')
class SiteImageSectionCreateView(CreateView):
    """Vista para crear una nueva sección de imágenes"""
    model = SiteImageSection
    form_class = SiteImageSectionForm
    template_name = 'site_images/site_image_section_form.html'
    success_url = reverse_lazy('site_images:image_management')

    def form_valid(self, form):
        messages.success(self.request, '¡Sección creada exitosamente!')
        return super().form_valid(form)


@method_decorator(permission_required('dashboard', 'editar'), name='dispatch')
class SiteImageSectionUpdateView(UpdateView):
    """Vista para editar una sección de imágenes"""
    model = SiteImageSection
    form_class = SiteImageSectionForm
    template_name = 'site_images/site_image_section_form.html'
    success_url = reverse_lazy('site_images:image_management')
    pk_url_kwarg = 'pk'

    def form_valid(self, form):
        messages.success(self.request, '¡Sección actualizada exitosamente!')
        return super().form_valid(form)


# ==================== IMÁGENES DEL SITIO ====================

@method_decorator(permission_required('dashboard', 'crear'), name='dispatch')
class SiteImageCreateView(CreateView):
    """Vista para crear una nueva imagen del sitio"""
    model = SiteImage
    form_class = SiteImageForm
    template_name = 'site_images/site_image_form.html'
    success_url = reverse_lazy('site_images:image_management')

    def get_initial(self):
        """Pre-seleccionar sección si viene el parámetro ?section=<id>"""
        initial = super().get_initial()
        section_id = self.request.GET.get('section')
        if section_id:
            try:
                initial['section'] = SiteImageSection.objects.get(pk=int(section_id))
            except (SiteImageSection.DoesNotExist, ValueError):
                pass
        return initial

    def form_valid(self, form):
        messages.success(self.request, '¡Imagen agregada exitosamente!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Error al agregar la imagen. Por favor, verifica los datos.')
        return super().form_invalid(form)


@method_decorator(permission_required('dashboard', 'editar'), name='dispatch')
class SiteImageUpdateView(UpdateView):
    """Vista para editar una imagen del sitio"""
    model = SiteImage
    form_class = SiteImageForm
    template_name = 'site_images/site_image_form.html'
    success_url = reverse_lazy('site_images:image_management')
    pk_url_kwarg = 'pk'

    def form_valid(self, form):
        messages.success(self.request, '¡Imagen actualizada exitosamente!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Error al actualizar la imagen. Por favor, verifica los datos.')
        return super().form_invalid(form)


@method_decorator(permission_required('dashboard', 'eliminar'), name='dispatch')
class SiteImageDeleteView(DeleteView):
    """Vista para eliminar una imagen del sitio"""
    model = SiteImage
    success_url = reverse_lazy('site_images:image_management')
    pk_url_kwarg = 'pk'

    def delete(self, request, *args, **kwargs):
        messages.success(request, '¡Imagen eliminada exitosamente!')
        return super().delete(request, *args, **kwargs)


@require_POST
@permission_required('dashboard', 'editar')
def site_image_toggle_active(request, pk):
    """Vista AJAX para activar/desactivar una imagen del sitio"""
    try:
        image = get_object_or_404(SiteImage, pk=pk)
        image.is_active = not image.is_active
        image.save()

        return JsonResponse({
            'success': True,
            'is_active': image.is_active,
            'message': 'Estado actualizado correctamente'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


# ==================== CONTENIDO DE LA HOME ====================

@method_decorator(permission_required('dashboard', 'editar'), name='dispatch')
class SiteContentListView(TemplateView):
    """Vista que muestra todas las secciones editables de la home"""
    template_name = 'site_images/site_content_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sections = []
        for section_key, defaults in SECTIONS_DEFAULT.items():
            obj, created = SiteContent.objects.get_or_create(
                section=section_key,
                defaults=defaults
            )
            sections.append(obj)
        context['sections'] = sections
        return context


@method_decorator(permission_required('dashboard', 'editar'), name='dispatch')
class SiteContentEditView(UpdateView):
    """Vista para editar el contenido de una sección de la home"""
    model = SiteContent
    form_class = SiteContentForm
    template_name = 'site_images/site_content_form.html'
    success_url = reverse_lazy('site_images:site_content_list')

    def get_object(self, queryset=None):
        section = self.kwargs['section']
        defaults = SECTIONS_DEFAULT.get(section, {})
        obj, _ = SiteContent.objects.get_or_create(section=section, defaults=defaults)
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section_label'] = self.object.get_section_display()
        context['section_key'] = self.object.section
        return context

    def form_valid(self, form):
        messages.success(self.request, f'¡Contenido de "{self.object.get_section_display()}" actualizado exitosamente!')
        return super().form_valid(form)
