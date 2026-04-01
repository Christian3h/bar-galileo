from django.core.management.base import BaseCommand
from site_images.models import SiteContent


INITIAL_DATA = {
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
        'service1_number': '5+',
        'service1_title': 'Años de experiencia',
        'service1_description': 'Perfeccionando el arte de la mixología y creando momentos únicos.',
        'service2_number': '150+',
        'service2_title': 'Cócteles únicos',
        'service2_description': 'Carta exclusiva con creaciones propias y clásicos reimaginados.',
        'service3_number': '24/7',
        'service3_title': 'Reservaciones',
        'service3_description': 'Sistema de reservas disponible las 24 horas para tu comodidad.',
        'service4_number': '100%',
        'service4_title': 'Satisfacción',
        'service4_description': 'Compromiso total con la excelencia en cada experiencia.',
    },
    'reservations': {
        'reservations_title': 'Reservas',
        'reservations_text': '¡Reserva tu mesa y asegura tu lugar en Bar Galileo!',
        'reservations_whatsapp': '573044029343',
        'reservations_button_text': 'Reservar por WhatsApp',
    },
}


class Command(BaseCommand):
    help = 'Inicializa el contenido de texto editable de la página de inicio'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Sobrescribe los valores existentes con los datos por defecto',
        )

    def handle(self, *args, **options):
        reset = options.get('reset', False)
        self.stdout.write(self.style.SUCCESS('Iniciando carga de contenido del sitio...'))

        created_count = 0
        updated_count = 0
        skipped_count = 0

        for section_key, defaults in INITIAL_DATA.items():
            if reset:
                obj, created = SiteContent.objects.update_or_create(
                    section=section_key,
                    defaults=defaults
                )
                if created:
                    created_count += 1
                    self.stdout.write(self.style.SUCCESS(f'✓ Creado: {obj.get_section_display()}'))
                else:
                    updated_count += 1
                    self.stdout.write(self.style.WARNING(f'↺ Actualizado: {obj.get_section_display()}'))
            else:
                obj, created = SiteContent.objects.get_or_create(
                    section=section_key,
                    defaults=defaults
                )
                if created:
                    created_count += 1
                    self.stdout.write(self.style.SUCCESS(f'✓ Creado: {obj.get_section_display()}'))
                else:
                    skipped_count += 1
                    self.stdout.write(self.style.WARNING(f'○ Ya existe: {obj.get_section_display()}'))

        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(self.style.SUCCESS(f'Registros creados: {created_count}'))
        if reset:
            self.stdout.write(self.style.WARNING(f'Registros actualizados: {updated_count}'))
        else:
            self.stdout.write(self.style.WARNING(f'Registros existentes (sin cambios): {skipped_count}'))
        self.stdout.write(self.style.SUCCESS('¡Contenido del sitio inicializado!'))
        self.stdout.write('=' * 50 + '\n')
