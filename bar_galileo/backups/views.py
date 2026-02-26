"""
Vistas para la gestión de backups de Bar Galileo.

Este módulo contiene las vistas basadas en clases (CBVs) para:
- Listar backups disponibles
- Crear backups (DB y Media)
- Descargar backups
- Eliminar backups antiguos
- Ver estadísticas de backups

Todas las vistas requieren permisos específicos del módulo 'backups'.
"""

from django.views.generic import TemplateView, View
from django.http import JsonResponse, FileResponse, Http404
from django.contrib import messages
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.conf import settings
from django.core.management import call_command
from roles.decorators import permission_required
from pathlib import Path
from datetime import datetime


@method_decorator(permission_required('backups', 'ver'), name='dispatch')
class BackupListView(TemplateView):
    """
    Vista para listar todos los backups disponibles.
    Muestra backups de DB y Media con sus tamaños y fechas.
    """
    template_name = 'backups/backup_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Directorios de backups
        db_backup_dir = Path(settings.BASE_DIR) / "backups" / "backup_files" / "db"
        media_backup_dir = Path(settings.BASE_DIR) / "backups" / "backup_files" / "media"

        # Listar backups de DB
        db_backups = []
        if db_backup_dir.exists():
            # Buscar archivos con y sin encriptación (.psql y .psql.gpg)
            for backup_file in sorted(db_backup_dir.glob('*.psql*'), reverse=True):
                db_backups.append({
                    'nombre': backup_file.name,
                    'fecha': datetime.fromtimestamp(backup_file.stat().st_mtime),
                    'tamanio': backup_file.stat().st_size,
                    'tamanio_mb': backup_file.stat().st_size / (1024 * 1024),
                    'tamanio_kb': backup_file.stat().st_size / 1024,
                    'path': str(backup_file),
                })

        # Listar backups de Media
        media_backups = []
        if media_backup_dir.exists():
            # Buscar archivos con y sin encriptación (.media.zip y .media.zip.gpg)
            for backup_file in sorted(media_backup_dir.glob('*.media.zip*'), reverse=True):
                media_backups.append({
                    'nombre': backup_file.name,
                    'fecha': datetime.fromtimestamp(backup_file.stat().st_mtime),
                    'tamanio': backup_file.stat().st_size,
                    'tamanio_mb': backup_file.stat().st_size / (1024 * 1024),
                    'path': str(backup_file),
                })

        # Estadísticas
        total_db_size = sum(b['tamanio'] for b in db_backups)
        total_media_size = sum(b['tamanio'] for b in media_backups)

        context.update({
            'db_backups': db_backups,
            'media_backups': media_backups,
            'total_db_backups': len(db_backups),
            'total_media_backups': len(media_backups),
            'total_db_size_mb': total_db_size / (1024 * 1024),
            'total_media_size_mb': total_media_size / (1024 * 1024),
            'total_size_mb': (total_db_size + total_media_size) / (1024 * 1024),
        })

        return context


@method_decorator(permission_required('backups', 'crear'), name='dispatch')
class BackupCreateView(View):
    """
    Vista para crear backups usando el comando personalizado.
    Usa el comando 'crear_backup_completo' que soluciona el bug de django-dbbackup.
    """

    def post(self, request):
        """
        Crea un backup completo (DB + Media) o parcial según los parámetros.
        """
        try:
            # Obtener parámetros
            tipo = request.POST.get('tipo', 'completo')  # completo, db, media

            # Crear backup según el tipo
            if tipo == 'db':
                call_command('crear_backup_completo', '--sin-media', verbosity=0)
                messages.success(request, '✅ Backup de base de datos creado exitosamente')
            elif tipo == 'media':
                call_command('crear_backup_completo', '--sin-db', verbosity=0)
                messages.success(request, '✅ Backup de archivos media creado exitosamente')
            else:  # completo
                call_command('crear_backup_completo', verbosity=0)
                messages.success(request, '✅ Backup completo creado exitosamente (DB + Media)')

            return JsonResponse({
                'success': True,
                'message': 'Backup creado exitosamente',
                'tipo': tipo
            })

        except ModuleNotFoundError as e:
            error_msg = f'❌ Error: Falta el módulo {str(e)}. Asegúrate de que el servidor esté usando el entorno virtual correcto.'
            messages.error(request, error_msg)
            return JsonResponse({
                'success': False,
                'error': error_msg
            }, status=500)
        except Exception as e:
            error_msg = f'❌ Error al crear backup: {str(e)}'
            messages.error(request, error_msg)
            return JsonResponse({
                'success': False,
                'error': error_msg
            }, status=500)


@method_decorator(permission_required('backups', 'crear'), name='dispatch')
class BackupDownloadView(View):
    """
    Vista para descargar un archivo de backup específico.
    Requiere permiso 'crear' ya que descargar es parte del flujo de creación de backups.
    """

    def get(self, request, tipo, filename):
        """
        Descarga un archivo de backup.

        Args:
            tipo: 'db' o 'media'
            filename: nombre del archivo de backup
        """
        try:
            # Determinar directorio según el tipo
            if tipo == 'db':
                backup_dir = Path(settings.BASE_DIR) / "backups" / "backup_files" / "db"
            elif tipo == 'media':
                backup_dir = Path(settings.BASE_DIR) / "backups" / "backup_files" / "media"
            else:
                raise Http404("Tipo de backup no válido")

            # Construir ruta del archivo
            file_path = backup_dir / filename

            # Verificar que el archivo existe y está dentro del directorio permitido
            if not file_path.exists() or not file_path.is_file():
                raise Http404("Archivo de backup no encontrado")

            if not file_path.resolve().is_relative_to(backup_dir.resolve()):
                raise Http404("Acceso denegado")

            # Servir el archivo
            response = FileResponse(
                open(file_path, 'rb'),
                as_attachment=True,
                filename=filename
            )
            response['Content-Type'] = 'application/octet-stream'
            response['Content-Length'] = file_path.stat().st_size

            return response

        except Http404:
            raise
        except Exception as e:
            messages.error(request, f'❌ Error al descargar backup: {str(e)}')
            return redirect('backups:backup_list')


@method_decorator(permission_required('backups', 'eliminar'), name='dispatch')
class BackupDeleteView(View):
    """
    Vista para eliminar un archivo de backup específico.
    """

    def post(self, request):
        """
        Elimina un archivo de backup.
        """
        try:
            tipo = request.POST.get('tipo')
            filename = request.POST.get('filename')

            if not tipo or not filename:
                return JsonResponse({
                    'success': False,
                    'error': 'Parámetros incompletos'
                }, status=400)

            # Determinar directorio según el tipo
            if tipo == 'db':
                backup_dir = Path(settings.BASE_DIR) / "backups" / "backup_files" / "db"
            elif tipo == 'media':
                backup_dir = Path(settings.BASE_DIR) / "backups" / "backup_files" / "media"
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Tipo de backup no válido'
                }, status=400)

            # Construir ruta del archivo
            file_path = backup_dir / filename

            # Verificar que el archivo existe y está dentro del directorio permitido
            if not file_path.exists() or not file_path.is_file():
                return JsonResponse({
                    'success': False,
                    'error': 'Archivo no encontrado'
                }, status=404)

            if not file_path.resolve().is_relative_to(backup_dir.resolve()):
                return JsonResponse({
                    'success': False,
                    'error': 'Acceso denegado'
                }, status=403)

            # Eliminar el archivo
            file_path.unlink()

            messages.success(request, f'✅ Backup eliminado: {filename}')
            return JsonResponse({
                'success': True,
                'message': f'Backup eliminado: {filename}'
            })

        except Exception as e:
            messages.error(request, f'❌ Error al eliminar backup: {str(e)}')
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


@method_decorator(permission_required('backups', 'ver'), name='dispatch')
class BackupStatsView(View):
    """
    Vista JSON con estadísticas de backups.
    Útil para gráficos y dashboards.
    """

    def get(self, request):
        """
        Retorna estadísticas en formato JSON.
        """
        try:
            db_backup_dir = Path(settings.BASE_DIR) / "backups" / "backup_files" / "db"
            media_backup_dir = Path(settings.BASE_DIR) / "backups" / "backup_files" / "media"

            # Contar y calcular tamaños
            db_backups = list(db_backup_dir.glob('*.psql.gpg')) if db_backup_dir.exists() else []
            media_backups = list(media_backup_dir.glob('*.media.zip.gpg')) if media_backup_dir.exists() else []

            total_db_size = sum(f.stat().st_size for f in db_backups)
            total_media_size = sum(f.stat().st_size for f in media_backups)

            # Último backup
            ultimo_db = max(db_backups, key=lambda f: f.stat().st_mtime) if db_backups else None
            ultimo_media = max(media_backups, key=lambda f: f.stat().st_mtime) if media_backups else None

            stats = {
                'total_backups': len(db_backups) + len(media_backups),
                'db_backups': {
                    'cantidad': len(db_backups),
                    'tamanio_total_mb': round(total_db_size / (1024 * 1024), 2),
                    'tamanio_promedio_kb': round((total_db_size / len(db_backups) / 1024) if db_backups else 0, 2),
                    'ultimo_backup': ultimo_db.name if ultimo_db else None,
                    'ultima_fecha': datetime.fromtimestamp(ultimo_db.stat().st_mtime).isoformat() if ultimo_db else None,
                },
                'media_backups': {
                    'cantidad': len(media_backups),
                    'tamanio_total_mb': round(total_media_size / (1024 * 1024), 2),
                    'tamanio_promedio_mb': round((total_media_size / len(media_backups) / (1024 * 1024)) if media_backups else 0, 2),
                    'ultimo_backup': ultimo_media.name if ultimo_media else None,
                    'ultima_fecha': datetime.fromtimestamp(ultimo_media.stat().st_mtime).isoformat() if ultimo_media else None,
                },
                'total_size_mb': round((total_db_size + total_media_size) / (1024 * 1024), 2),
            }

            return JsonResponse(stats)

        except Exception as e:
            return JsonResponse({
                'error': str(e)
            }, status=500)


@method_decorator(permission_required('backups', 'editar'), name='dispatch')
class BackupRestoreView(View):
    """
    Vista para restaurar un backup (base de datos o media).
    Requiere permiso 'editar' ya que restaurar modifica datos del sistema.
    Utiliza los comandos de django-dbbackup para restaurar correctamente.
    """

    def post(self, request):
        """
        Restaura un backup específico desencriptando manualmente antes de restaurar.
        
        Esta implementación evita el problema de passphrase interactiva de GPG
        desencriptando manualmente el archivo antes de pasarlo a django-dbbackup.
        """
        import logging
        import subprocess
        import os
        
        logger = logging.getLogger(__name__)
        decrypted_file_path = None  # Para limpieza posterior
        
        try:
            tipo = request.POST.get('tipo')
            filename = request.POST.get('filename')
            
            logger.info(f"=== INICIO RESTAURACIÓN ===")
            logger.info(f"Tipo: {tipo}")
            logger.info(f"Archivo: {filename}")

            if not tipo or not filename:
                logger.error("Parámetros incompletos")
                return JsonResponse({
                    'success': False,
                    'error': 'Parámetros incompletos'
                }, status=400)

            # Determinar directorio según el tipo
            if tipo == 'db':
                backup_dir = Path(settings.BASE_DIR) / "backups" / "backup_files" / "db"
                comando = 'dbrestore'
            elif tipo == 'media':
                backup_dir = Path(settings.BASE_DIR) / "backups" / "backup_files" / "media"
                comando = 'mediarestore'
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Tipo de backup no válido'
                }, status=400)

            # Construir ruta del archivo
            file_path = backup_dir / filename
            logger.info(f"Ruta del archivo: {file_path}")
            logger.info(f"Existe: {file_path.exists()}")

            # Verificar que el archivo existe
            if not file_path.exists() or not file_path.is_file():
                logger.error(f"Archivo no encontrado: {file_path}")
                return JsonResponse({
                    'success': False,
                    'error': f'Archivo no encontrado: {filename}'
                }, status=404)

            if not file_path.resolve().is_relative_to(backup_dir.resolve()):
                logger.error("Acceso denegado")
                return JsonResponse({
                    'success': False,
                    'error': 'Acceso denegado'
                }, status=403)

            # PASO 1: Desencriptar manualmente si el archivo está encriptado
            if filename.endswith('.gpg'):
                logger.info("Archivo encriptado detectado, desencriptando manualmente...")
                
                # Nombre del archivo desencriptado
                decrypted_filename = filename[:-4]  # Remover .gpg
                decrypted_file_path = backup_dir / decrypted_filename
                
                # Comando GPG en modo batch (sin interacción)
                gpg_command = [
                    'gpg',
                    '--batch',              # Modo no interactivo
                    '--yes',                # Responder sí automáticamente
                    '--quiet',              # Silencioso
                    '--no-tty',             # Sin terminal
                    '--passphrase', '',     # Passphrase vacía (clave sin contraseña)
                    '--pinentry-mode', 'loopback',  # Sin pinentry interactivo
                    '--decrypt',
                    '--output', str(decrypted_file_path),
                    str(file_path)
                ]
                
                logger.info(f"Ejecutando GPG desencriptación: gpg --decrypt {file_path}")
                
                try:
                    result = subprocess.run(
                        gpg_command,
                        check=True,
                        capture_output=True,
                        text=True,
                        timeout=60,  # Timeout de 60 segundos
                        stdin=subprocess.DEVNULL  # No leer de stdin
                    )
                    logger.info(f"Desencriptación exitosa: {decrypted_file_path}")
                    
                    # Verificar que el archivo desencriptado existe
                    if not decrypted_file_path.exists():
                        raise Exception("El archivo desencriptado no se creó correctamente")
                    
                except subprocess.TimeoutExpired:
                    logger.error("Timeout en desencriptación GPG")
                    raise Exception("La desencriptación GPG excedió el tiempo límite de 60 segundos")
                    
                except subprocess.CalledProcessError as e:
                    logger.error(f"Error en desencriptación GPG: {e.stderr}")
                    raise Exception(f"Error al desencriptar con GPG: {e.stderr}")
                
                # Usar el archivo desencriptado para la restauración
                restore_filename = decrypted_filename
                
            else:
                # Archivo no encriptado, usar directamente
                logger.info("Archivo no encriptado, restaurando directamente...")
                restore_filename = filename

            # PASO 2: Restaurar el backup
            logger.info(f"Iniciando restauración con archivo: {restore_filename}")

            try:
                if tipo == 'db':
                    # Restaurar base de datos con MySQLdb (Python puro, sin binarios externos)
                    logger.info(f"Restaurando DB con MySQLdb desde: {restore_filename}")
                    import MySQLdb

                    db_config = settings.DATABASES['default']
                    restore_file_path = backup_dir / restore_filename

                    conn = MySQLdb.connect(
                        host=db_config.get('HOST', 'localhost'),
                        port=int(db_config.get('PORT', 3306)),
                        user=db_config.get('USER', 'root'),
                        passwd=db_config.get('PASSWORD', ''),
                        db=db_config['NAME'],
                        charset='utf8mb4',
                    )

                    try:
                        cursor = conn.cursor()
                        cursor.execute("SET FOREIGN_KEY_CHECKS=0;")

                        with open(restore_file_path, 'r', encoding='utf-8') as f:
                            sql_content = f.read()

                        # Dividir el contenido en sentencias individuales
                        # Ignorar líneas de comentarios y vacías
                        statements = []
                        current = []
                        for line in sql_content.splitlines():
                            stripped = line.strip()
                            if stripped.startswith('--') or stripped == '':
                                continue
                            current.append(line)
                            if stripped.endswith(';'):
                                stmt = '\n'.join(current).strip()
                                if stmt:
                                    statements.append(stmt)
                                current = []

                        logger.info(f"Ejecutando {len(statements)} sentencias SQL...")
                        errores_sql = 0
                        for i, stmt in enumerate(statements):
                            try:
                                cursor.execute(stmt)
                            except Exception as e_sql:
                                errores_sql += 1
                                logger.warning(f"Sentencia {i+1} con error (ignorado): {str(e_sql)[:200]}")

                        conn.commit()
                        cursor.execute("SET FOREIGN_KEY_CHECKS=1;")
                        cursor.close()
                        logger.info(f"Restauración completada. Errores ignorados: {errores_sql}")
                    finally:
                        conn.close()

                    logger.info("Restauración de DB completada exitosamente")

                elif tipo == 'media':
                    # Restaurar archivos media extrayendo el archivo directamente a MEDIA_ROOT.
                    # django-dbbackup guarda el media como TAR (aunque usa extensión .zip),
                    # por lo que se usa tarfile. Si falla, se intenta con zipfile como fallback.
                    import tarfile
                    import zipfile
                    restore_file_path = backup_dir / restore_filename
                    media_root = Path(settings.MEDIA_ROOT)
                    media_root.mkdir(parents=True, exist_ok=True)

                    logger.info(f"Extrayendo {restore_file_path} en {media_root} ...")

                    if tarfile.is_tarfile(str(restore_file_path)):
                        with tarfile.open(restore_file_path, 'r:*') as tf:
                            tf.extractall(media_root)
                        logger.info("Restauración de media (TAR) completada exitosamente")
                    elif zipfile.is_zipfile(restore_file_path):
                        with zipfile.ZipFile(restore_file_path, 'r') as zf:
                            zf.extractall(media_root)
                        logger.info("Restauración de media (ZIP) completada exitosamente")
                    else:
                        raise Exception(
                            f"El archivo '{restore_filename}' no es un TAR ni ZIP válido."
                        )

            except Exception as e:
                logger.error(f"Error durante la ejecución del comando: {str(e)}")
                import traceback
                logger.error(traceback.format_exc())
                raise Exception(f"Error durante la restauración: {str(e)}")

            # PASO 3: Limpiar archivo desencriptado por seguridad
            if decrypted_file_path and decrypted_file_path.exists():
                logger.info(f"Eliminando archivo desencriptado temporal: {decrypted_file_path}")
                decrypted_file_path.unlink()
                logger.info("Archivo temporal eliminado exitosamente")

            logger.info(f"=== RESTAURACIÓN COMPLETADA ===")
            messages.success(request, f'✅ Backup restaurado exitosamente: {filename}')
            return JsonResponse({
                'success': True,
                'message': f'Backup restaurado: {filename}'
            })

        except Exception as e:
            # Limpiar archivo desencriptado en caso de error
            if decrypted_file_path and decrypted_file_path.exists():
                logger.warning(f"Limpiando archivo desencriptado debido a error: {decrypted_file_path}")
                try:
                    decrypted_file_path.unlink()
                except:
                    pass
            
            logger.error(f"Error general al restaurar backup: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            messages.error(request, f'❌ Error al restaurar backup: {str(e)}')
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


@method_decorator(permission_required('backups', 'editar'), name='dispatch')
class BackupUploadView(View):
    """
    Vista para subir archivos de backup.
    Acepta archivos .psql.gpg (DB) o .media.zip.gpg (Media).
    """

    def post(self, request):
        """
        Sube un archivo de backup al servidor.
        """
        try:
            if 'backup_file' not in request.FILES:
                return JsonResponse({
                    'success': False,
                    'error': 'No se proporcionó ningún archivo'
                }, status=400)

            backup_file = request.FILES['backup_file']
            filename = backup_file.name

            # Validar extensión - aceptar diferentes formatos de backups GPG
            if filename.endswith('.psql.gpg') or filename.endswith('.sql.gpg') or \
               filename.endswith('.mysql.gpg') or (filename.endswith('.gpg') and 'db' in filename.lower()):
                tipo = 'db'
                backup_dir = Path(settings.BASE_DIR) / "backups" / "backup_files" / "db"
                # Normalizar nombre del archivo a formato estándar
                if not filename.endswith('.psql.gpg'):
                    # Mantener el nombre original pero en la carpeta correcta
                    pass
            elif filename.endswith('.media.zip.gpg') or filename.endswith('.zip.gpg') or \
                 (filename.endswith('.gpg') and 'media' in filename.lower()):
                tipo = 'media'
                backup_dir = Path(settings.BASE_DIR) / "backups" / "backup_files" / "media"
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Tipo de archivo no válido. Debe ser un backup encriptado (.psql.gpg, .sql.gpg, .zip.gpg, .media.zip.gpg)'
                }, status=400)

            # Crear directorio si no existe
            backup_dir.mkdir(parents=True, exist_ok=True)

            # Guardar archivo
            file_path = backup_dir / filename

            # Evitar sobrescribir archivos existentes
            if file_path.exists():
                return JsonResponse({
                    'success': False,
                    'error': f'Ya existe un archivo con el nombre {filename}'
                }, status=400)

            # Escribir archivo en chunks
            with open(file_path, 'wb+') as destination:
                for chunk in backup_file.chunks():
                    destination.write(chunk)

            messages.success(request, f'✅ Backup subido exitosamente: {filename}')
            return JsonResponse({
                'success': True,
                'message': f'Backup subido: {filename}',
                'tipo': tipo,
                'filename': filename
            })

        except Exception as e:
            messages.error(request, f'❌ Error al subir backup: {str(e)}')
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
