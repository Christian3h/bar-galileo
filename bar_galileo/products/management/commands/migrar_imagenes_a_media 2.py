"""
Comando para migrar imágenes de productos desde static/ a media/
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from products.models import ProductoImagen, Producto
import os
import shutil


class Command(BaseCommand):
    help = 'Migra las imágenes de productos de static/img/productos/ a media/productos/'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Iniciando migración de imágenes...'))

        # Directorios
        static_dir = os.path.join(settings.BASE_DIR, 'static', 'img', 'productos')
        media_dir = os.path.join(settings.MEDIA_ROOT, 'productos')

        # Crear directorio media/productos si no existe
        os.makedirs(media_dir, exist_ok=True)

        migradas = 0
        errores = 0

        # Obtener todas las imágenes de productos
        imagenes = ProductoImagen.objects.all()
        total = imagenes.count()

        self.stdout.write(f'Total de imágenes a migrar: {total}')

        for imagen in imagenes:
            try:
                # Obtener la ruta actual como string
                ruta_antigua = str(imagen.imagen)

                # Si ya está en el formato correcto (solo productos/...), skip
                if ruta_antigua.startswith('productos/'):
                    self.stdout.write(
                        self.style.WARNING(f'  Ya migrada: {ruta_antigua}')
                    )
                    continue

                # Extraer la ruta desde static/
                if ruta_antigua.startswith('img/productos/'):
                    ruta_relativa = ruta_antigua.replace('img/productos/', '')
                else:
                    ruta_relativa = ruta_antigua

                archivo_origen = os.path.join(static_dir, ruta_relativa)
                archivo_destino = os.path.join(media_dir, ruta_relativa)

                # Verificar que el archivo origen existe
                if not os.path.exists(archivo_origen):
                    self.stdout.write(
                        self.style.WARNING(f'  Archivo no encontrado: {archivo_origen}')
                    )
                    continue

                # Crear directorio destino si no existe
                os.makedirs(os.path.dirname(archivo_destino), exist_ok=True)

                # Copiar archivo
                shutil.copy2(archivo_origen, archivo_destino)

                # Actualizar la ruta en la base de datos
                # Ahora solo necesita "productos/{id}/{nombre}.webp"
                nueva_ruta = f"productos/{ruta_relativa}"
                imagen.imagen = nueva_ruta
                imagen.save()

                migradas += 1
                self.stdout.write(
                    self.style.SUCCESS(f'  ✓ Migrada: {ruta_antigua} → {nueva_ruta}')
                )

            except Exception as e:
                errores += 1
                self.stdout.write(
                    self.style.ERROR(f'  ✗ Error al migrar {imagen.id_imagen}: {str(e)}')
                )

        self.stdout.write(self.style.SUCCESS(f'\n=== Resumen ==='))
        self.stdout.write(f'Total: {total}')
        self.stdout.write(self.style.SUCCESS(f'Migradas: {migradas}'))
        if errores > 0:
            self.stdout.write(self.style.ERROR(f'Errores: {errores}'))

        self.stdout.write(self.style.SUCCESS('\n¡Migración completada!'))
        self.stdout.write(self.style.WARNING(
            '\nRecuerda ejecutar: python manage.py migrate products'
        ))
