"""
URLs para la aplicación de backups.

Rutas disponibles:
- /backups/ - Listar backups
- /backups/crear/ - Crear nuevo backup
- /backups/descargar/<tipo>/<filename>/ - Descargar backup
- /backups/eliminar/ - Eliminar backup
- /backups/stats/ - Estadísticas JSON
"""

from django.urls import path
from .views import (
    BackupListView,
    BackupCreateView,
    BackupDownloadView,
    BackupDeleteView,
    BackupStatsView,
    BackupRestoreView,
    BackupUploadView,
)

app_name = 'backups'

urlpatterns = [
    # Vista principal - Listar backups
    path('', BackupListView.as_view(), name='backup_list'),

    # Crear backup
    path('crear/', BackupCreateView.as_view(), name='backup_create'),

    # Descargar backup
    path('descargar/<str:tipo>/<str:filename>/', BackupDownloadView.as_view(), name='backup_download'),

    # Eliminar backup
    path('eliminar/', BackupDeleteView.as_view(), name='backup_delete'),

    # Subir backup
    path('subir/', BackupUploadView.as_view(), name='backup_upload'),

    # Restaurar backup
    path('restaurar/', BackupRestoreView.as_view(), name='backup_restore'),

    # Estadísticas JSON
    path('stats/', BackupStatsView.as_view(), name='backup_stats'),
]
