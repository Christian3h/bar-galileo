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
            for backup_file in sorted(db_backup_dir.glob('*.psql.gpg'), reverse=True):
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
            for backup_file in sorted(media_backup_dir.glob('*.media.zip.gpg'), reverse=True):
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

        except Exception as e:
            messages.error(request, f'❌ Error al crear backup: {str(e)}')
            return JsonResponse({
                'success': False,
                'error': str(e)
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
    """

    def post(self, request):
        """
        Restaura un backup específico.
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

            # Verificar que el archivo existe
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

            # Restaurar el backup desencriptando primero
            try:
                import subprocess
                import os

                if tipo == 'db':
                    # Desencriptar y restaurar base de datos
                    db_path = Path(settings.BASE_DIR) / "db.sqlite3"
                    import shutil

                    # Crear backup de la BD actual
                    backup_current = db_path.with_suffix('.sqlite3.backup')
                    if db_path.exists():
                        shutil.copy2(db_path, backup_current)
                        # Eliminar el archivo actual para evitar pregunta de sobrescritura
                        db_path.unlink()

                    # Desencriptar el backup con GPG
                    result = subprocess.run(
                        ['gpg', '--output', str(db_path), '--decrypt', str(file_path)],
                        capture_output=True,
                        text=True
                    )

                    if result.returncode != 0:
                        # Restaurar backup anterior si falla
                        if backup_current.exists():
                            shutil.copy2(backup_current, db_path)
                        raise Exception(f"Error al desencriptar: {result.stderr}")

                    # Eliminar backup temporal si todo salió bien
                    if backup_current.exists():
                        backup_current.unlink()

                elif tipo == 'media':
                    # Desencriptar y restaurar media
                    media_root = Path(settings.MEDIA_ROOT)

                    # Crear archivo temporal desencriptado
                    import tempfile
                    with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp_file:
                        tmp_path = Path(tmp_file.name)

                    # Desencriptar el zip
                    result = subprocess.run(
                        ['gpg', '--output', str(tmp_path), '--decrypt', str(file_path)],
                        capture_output=True,
                        text=True
                    )

                    if result.returncode != 0:
                        tmp_path.unlink()
                        raise Exception(f"Error al desencriptar: {result.stderr}")

                    # Extraer el zip
                    import zipfile
                    with zipfile.ZipFile(tmp_path, 'r') as zip_ref:
                        zip_ref.extractall(media_root)

                    # Eliminar archivo temporal
                    tmp_path.unlink()

            except subprocess.CalledProcessError as e:
                raise Exception(f"Error en el proceso de restauración: {str(e)}")
            except Exception as e:
                raise Exception(f"Error durante la restauración: {str(e)}")

            messages.success(request, f'✅ Backup restaurado exitosamente: {filename}')
            return JsonResponse({
                'success': True,
                'message': f'Backup restaurado: {filename}'
            })

        except Exception as e:
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

            # Validar extensión
            if filename.endswith('.psql.gpg'):
                tipo = 'db'
                backup_dir = Path(settings.BASE_DIR) / "backups" / "backup_files" / "db"
            elif filename.endswith('.media.zip.gpg'):
                tipo = 'media'
                backup_dir = Path(settings.BASE_DIR) / "backups" / "backup_files" / "media"
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Tipo de archivo no válido. Debe ser .psql.gpg o .media.zip.gpg'
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
