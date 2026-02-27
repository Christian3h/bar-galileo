"""
Comando para crear backups completos (DB + Media).
Implementa el backup de MySQL directamente con Python (MySQLdb),
sin ejecutar binarios externos, para evitar problemas de permisos/PATH
cuando se ejecuta desde el servidor web (uvicorn/ASGI).

Uso:
    python manage.py crear_backup_completo
"""

from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
from pathlib import Path
from datetime import datetime
import os
import shutil


class Command(BaseCommand):
    help = 'Crea un backup completo de la base de datos y archivos media'

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

    def _crear_backup_mysql(self, db_backup_dir):
        """
        Crea un dump de MySQL usando MySQLdb (Python puro).
        No requiere ejecutar ningún binario externo (mysqldump).
        Devuelve el Path del archivo creado.
        """
        import MySQLdb

        db = settings.DATABASES['default']
        timestamp = datetime.now().strftime('%Y-%m-%d-%H%M%S')
        output_file = db_backup_dir / f'{timestamp}.psql'

        conn = MySQLdb.connect(
            host=db.get('HOST', 'localhost'),
            port=int(db.get('PORT', 3306)),
            user=db.get('USER', 'root'),
            passwd=db.get('PASSWORD', ''),
            db=db['NAME'],
            charset='utf8mb4',
        )

        try:
            cursor = conn.cursor()
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f'-- Backup de {db["NAME"]} generado el {datetime.now()}\n')
                f.write('SET FOREIGN_KEY_CHECKS=0;\n')
                f.write('SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";\n')
                f.write('SET NAMES utf8mb4;\n\n')

                # Obtener lista de tablas
                cursor.execute('SHOW TABLES')
                tablas = [row[0] for row in cursor.fetchall()]

                for tabla in tablas:
                    # CREATE TABLE
                    cursor.execute(f'SHOW CREATE TABLE `{tabla}`')
                    create_sql = cursor.fetchone()[1]
                    f.write(f'DROP TABLE IF EXISTS `{tabla}`;\n')
                    f.write(f'{create_sql};\n\n')

                    # Datos en lotes de 500 filas
                    cursor.execute(f'SELECT * FROM `{tabla}`')
                    columnas = [col[0] for col in cursor.description]
                    col_list = ', '.join(f'`{c}`' for c in columnas)
                    filas = cursor.fetchmany(500)
                    while filas:
                        valores_lista = []
                        for fila in filas:
                            valores = []
                            for v in fila:
                                if v is None:
                                    valores.append('NULL')
                                elif isinstance(v, (int, float)):
                                    valores.append(str(v))
                                elif isinstance(v, bytes):
                                    valores.append(
                                        '0x' + v.hex() if v else "''"
                                    )
                                else:
                                    escaped = str(v).replace('\\', '\\\\').replace("'", "\\'")
                                    valores.append(f"'{escaped}'")
                            valores_lista.append(f"({', '.join(valores)})")
                        f.write(
                            f'INSERT INTO `{tabla}` ({col_list}) VALUES\n'
                            + ',\n'.join(valores_lista)
                            + ';\n'
                        )
                        filas = cursor.fetchmany(500)
                    f.write('\n')

                f.write('SET FOREIGN_KEY_CHECKS=1;\n')

            cursor.close()
        finally:
            conn.close()

        return output_file

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

        # Rastrear errores para propagar al final
        errores = []

        # 1. Backup de Base de Datos
        if not options['sin_db']:
            self.stdout.write(self.style.WARNING('📊 Creando backup de base de datos...'))
            try:
                backup_file = self._crear_backup_mysql(db_backup_dir)
                self.stdout.write(self.style.SUCCESS(f'✅ Backup de DB creado: {backup_file.name}'))
                self.stdout.write(f'   Tamaño: {backup_file.stat().st_size / 1024:.2f} KB')
            except Exception as e:
                msg = str(e)
                self.stdout.write(self.style.ERROR(f'❌ Error al crear backup de DB: {msg}'))
                errores.append(f'Backup DB: {msg}')
        else:
            self.stdout.write(self.style.WARNING('⏭️  Saltando backup de base de datos'))

        self.stdout.write('')

        # 2. Backup de Media
        if not options['sin_media']:
            self.stdout.write(self.style.WARNING('📁 Creando backup de archivos media...'))
            pattern_media = '*.media.zip.gpg' if settings.DBBACKUP_ENCRYPTION else '*.media.zip'
            archivos_antes_media = set(media_backup_dir.glob(pattern_media))
            try:
                if settings.DBBACKUP_ENCRYPTION:
                    call_command('mediabackup', '--encrypt', verbosity=1)
                else:
                    call_command('mediabackup', verbosity=1)

                # WORKAROUND: Mover el archivo de media de db/ a media/ si es necesario
                # debido al bug en django-dbbackup 5.0.0
                media_files_in_db = sorted(db_backup_dir.glob(pattern_media))
                if media_files_in_db:
                    for media_file in media_files_in_db:
                        destino = media_backup_dir / media_file.name
                        shutil.move(str(media_file), str(destino))
                        self.stdout.write(self.style.SUCCESS(f'✅ Backup de Media creado: {destino.name}'))
                        self.stdout.write(f'   Tamaño: {destino.stat().st_size / (1024 * 1024):.2f} MB')
                        self.stdout.write(f'   📂 Movido a: backups/backup_files/media/')
                else:
                    # Detectar si se creó un archivo nuevo en la carpeta correcta
                    archivos_despues_media = set(media_backup_dir.glob(pattern_media))
                    nuevos_media = archivos_despues_media - archivos_antes_media
                    if nuevos_media:
                        ultimo_media = sorted(nuevos_media)[-1]
                        self.stdout.write(self.style.SUCCESS(f'✅ Backup de Media: {ultimo_media.name}'))
                        self.stdout.write(f'   Tamaño: {ultimo_media.stat().st_size / (1024 * 1024):.2f} MB')
                    else:
                        msg = 'El comando mediabackup se ejecutó pero no se encontró el archivo de backup'
                        self.stdout.write(self.style.ERROR(f'❌ {msg}'))
                        errores.append(f'Backup Media: {msg}')
            except Exception as e:
                msg = str(e)
                self.stdout.write(self.style.ERROR(f'❌ Error al crear backup de Media: {msg}'))
                errores.append(f'Backup Media: {msg}')
        else:
            self.stdout.write(self.style.WARNING('⏭️  Saltando backup de archivos media'))

        self.stdout.write('')
        if errores:
            self.stdout.write(self.style.ERROR('=' * 70))
            self.stdout.write(self.style.ERROR('❌ PROCESO COMPLETADO CON ERRORES'))
            self.stdout.write(self.style.ERROR('=' * 70))
        else:
            self.stdout.write(self.style.SUCCESS('=' * 70))
            self.stdout.write(self.style.SUCCESS('✅ PROCESO DE BACKUP COMPLETADO'))
            self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write('')

        # Resumen de backups
        self.stdout.write(self.style.WARNING('📋 RESUMEN DE BACKUPS DISPONIBLES:'))
        self.stdout.write('')
        db_backups = sorted(db_backup_dir.glob('*.psql*'))
        if db_backups:
            self.stdout.write(f'  🗄️  Backups de Base de Datos ({len(db_backups)}):')
            for backup in db_backups[-3:]:  # Mostrar últimos 3
                fecha = backup.stem.replace('.psql', '')
                tamanio = backup.stat().st_size / 1024
                self.stdout.write(f'     • {fecha} ({tamanio:.2f} KB)')

        self.stdout.write('')

        media_backups = sorted(media_backup_dir.glob('*.media.zip*'))
        if media_backups:
            self.stdout.write(f'  📸 Backups de Media ({len(media_backups)}):')
            for backup in media_backups[-3:]:  # Mostrar últimos 3
                fecha = backup.stem.replace('.media.zip', '')
                tamanio = backup.stat().st_size / (1024 * 1024)
                self.stdout.write(f'     • {fecha} ({tamanio:.2f} MB)')

        self.stdout.write('')

        # Elevar excepción DESPUÉS del resumen para que el llamador (la vista) pueda reportar el error
        if errores:
            raise RuntimeError('\n'.join(errores))

