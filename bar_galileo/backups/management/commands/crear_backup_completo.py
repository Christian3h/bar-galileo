"""
Comando para crear backups completos (DB + Media) con encriptación GPG.
Soluciona el problema de django-dbbackup 5.0.0 donde los backups de media
se guardan en la carpeta incorrecta.

Uso:
    python manage.py crear_backup_completo
"""

from django.core.management.base import BaseCommand
from django.core.management import call_command
from pathlib import Path
from django.conf import settings
import os
import shutil
from datetime import datetime


class Command(BaseCommand):
    help = 'Crea un backup completo de la base de datos y archivos media con encriptación GPG'

    def add_arguments(self, parser):
        parser.add_argument(
            '--sin-db',
            action='store_true',
            help='No crear backup de la base de datos',
        )
        parser.add_argument(
            '--sin-media',
            action='store_true',
            help='No crear backup de archivos media',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('CREANDO BACKUP COMPLETO DE BAR GALILEO'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write('')

        # Directorios de destino
        db_backup_dir = Path(settings.BASE_DIR) / "backups" / "backup_files" / "db"
        media_backup_dir = Path(settings.BASE_DIR) / "backups" / "backup_files" / "media"

        # Asegurar que existen los directorios
        db_backup_dir.mkdir(parents=True, exist_ok=True)
        media_backup_dir.mkdir(parents=True, exist_ok=True)

        # 1. Backup de Base de Datos
        if not options['sin_db']:
            self.stdout.write(self.style.WARNING('📊 Creando backup de base de datos...'))
            try:
                call_command('dbbackup', '--encrypt', verbosity=1)

                # Verificar que se creó en la carpeta correcta
                db_files = sorted(db_backup_dir.glob('*.psql.gpg'))
                if db_files:
                    ultimo_db = db_files[-1]
                    self.stdout.write(self.style.SUCCESS(f'✅ Backup de DB creado: {ultimo_db.name}'))
                    self.stdout.write(f'   Tamaño: {ultimo_db.stat().st_size / 1024:.2f} KB')
                else:
                    self.stdout.write(self.style.ERROR('❌ No se encontró el backup de DB'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Error al crear backup de DB: {e}'))
        else:
            self.stdout.write(self.style.WARNING('⏭️  Saltando backup de base de datos'))

        self.stdout.write('')

        # 2. Backup de Media
        if not options['sin_media']:
            self.stdout.write(self.style.WARNING('📁 Creando backup de archivos media...'))
            try:
                # Crear el backup de media
                call_command('mediabackup', '--encrypt', verbosity=1)

                # WORKAROUND: Mover el archivo de media de db/ a media/ si es necesario
                # debido al bug en django-dbbackup 5.0.0
                media_files_in_db = sorted(db_backup_dir.glob('*.media.zip.gpg'))
                if media_files_in_db:
                    for media_file in media_files_in_db:
                        destino = media_backup_dir / media_file.name
                        shutil.move(str(media_file), str(destino))
                        self.stdout.write(self.style.SUCCESS(f'✅ Backup de Media creado: {destino.name}'))
                        self.stdout.write(f'   Tamaño: {destino.stat().st_size / (1024 * 1024):.2f} MB')
                        self.stdout.write(f'   📂 Movido a: backups/backup_files/media/')
                else:
                    # Verificar si ya está en la carpeta correcta
                    media_files = sorted(media_backup_dir.glob('*.media.zip.gpg'))
                    if media_files:
                        ultimo_media = media_files[-1]
                        self.stdout.write(self.style.SUCCESS(f'✅ Backup de Media: {ultimo_media.name}'))
                        self.stdout.write(f'   Tamaño: {ultimo_media.stat().st_size / (1024 * 1024):.2f} MB')
                    else:
                        self.stdout.write(self.style.ERROR('❌ No se encontró el backup de Media'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Error al crear backup de Media: {e}'))
        else:
            self.stdout.write(self.style.WARNING('⏭️  Saltando backup de archivos media'))

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('✅ PROCESO DE BACKUP COMPLETADO'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write('')

        # Resumen de backups
        self.stdout.write(self.style.WARNING('📋 RESUMEN DE BACKUPS DISPONIBLES:'))
        self.stdout.write('')

        db_backups = sorted(db_backup_dir.glob('*.psql.gpg'))
        if db_backups:
            self.stdout.write(f'  🗄️  Backups de Base de Datos ({len(db_backups)}):')
            for backup in db_backups[-3:]:  # Mostrar últimos 3
                fecha = backup.stem.replace('.psql', '')
                tamanio = backup.stat().st_size / 1024
                self.stdout.write(f'     • {fecha} ({tamanio:.2f} KB)')

        self.stdout.write('')

        media_backups = sorted(media_backup_dir.glob('*.media.zip.gpg'))
        if media_backups:
            self.stdout.write(f'  📸 Backups de Media ({len(media_backups)}):')
            for backup in media_backups[-3:]:  # Mostrar últimos 3
                fecha = backup.stem.replace('.media.zip', '')
                tamanio = backup.stat().st_size / (1024 * 1024)
                self.stdout.write(f'     • {fecha} ({tamanio:.2f} MB)')

        self.stdout.write('')
