from django.core.management.base import BaseCommand
from admin_dashboard.models import SiteImageSection


class Command(BaseCommand):
    help = 'Inicializa las secciones predefinidas de imágenes del sitio'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando creación de secciones predefinidas...'))
        
        sections_data = [
            {
                'name': 'Carrusel Principal - Hero',
                'section_type': 'hero_carousel',
                'description': 'Imágenes que se muestran en el carrusel de la sección hero de la página principal'
            },
            {
                'name': 'Sección Acerca de',
                'section_type': 'about',
                'description': 'Imagen principal de la sección "Acerca de" en la página de inicio'
            },
            {
                'name': 'Banner Promocional',
                'section_type': 'banner',
                'description': 'Banners promocionales que se pueden mostrar en diferentes partes del sitio'
            },
            {
                'name': 'Iconos de Servicios',
                'section_type': 'icon',
                'description': 'Iconos utilizados en la sección de servicios y características'
            },
            {
                'name': 'Fondo de Página',
                'section_type': 'background',
                'description': 'Imágenes de fondo para diferentes secciones del sitio'
            },
            {
                'name': 'Logo y Header',
                'section_type': 'header',
                'description': 'Imágenes del encabezado incluyendo logos y elementos decorativos'
            },
            {
                'name': 'Pie de Página',
                'section_type': 'footer',
                'description': 'Imágenes y logos del pie de página'
            },
        ]
        
        created_count = 0
        skipped_count = 0
        
        for section_data in sections_data:
            section, created = SiteImageSection.objects.get_or_create(
                name=section_data['name'],
                defaults={
                    'section_type': section_data['section_type'],
                    'description': section_data['description']
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Sección creada: {section.name}')
                )
            else:
                skipped_count += 1
                self.stdout.write(
                    self.style.WARNING(f'○ Sección ya existe: {section.name}')
                )
        
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS(f'Secciones creadas: {created_count}'))
        self.stdout.write(self.style.WARNING(f'Secciones existentes: {skipped_count}'))
        self.stdout.write(self.style.SUCCESS('¡Inicialización completada!'))
        self.stdout.write('='*50 + '\n')
