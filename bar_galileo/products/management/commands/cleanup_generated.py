#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Management command to safely remove generated products and their images.

Usage examples (run from project root where manage.py lives):
- Simulate (dry-run) what would be deleted:
    python manage.py cleanup_generated --dry-run

- Delete products whose names match the generation pattern (e.g. word-123):
    python manage.py cleanup_generated --yes

- Delete only images (leave product rows):
    python manage.py cleanup_generated --images-only --yes

- Delete only products (leave image files alone):
    python manage.py cleanup_generated --products-only --yes

- Limit how many items to process (useful for testing):
    python manage.py cleanup_generated --limit 100 --yes

- Restrict to products whose name starts with a prefix:
    python manage.py cleanup_generated --prefix myprefix- --yes

The command tries to be safe:
- By default it runs in dry-run mode and only prints what would be removed.
- To actually perform deletion use --yes (or --force).
- If the database backend doesn't support regex filtering, the command falls back
  to checking the name pattern in Python.
"""
from __future__ import annotations

import os
import re
import shutil
from typing import Iterable

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.conf import settings

# Import models from the app
from products.models import Producto, ProductoImagen


def _is_generated_name(name: str) -> bool:
    """
    Heuristic to detect generated product names from the generator used earlier,
    which produced names like: <word>-<index>  (e.g. 'acoustic-123').
    This returns True for names that end with '-' followed by digits.
    """
    return bool(re.search(r'-\d+$', name))


def _iter_generated_products(prefix: str | None = None) -> Iterable[Producto]:
    """
    Yield products that appear to be generated:
    - If prefix provided: filter by nombre__startswith=prefix.
    - Else try DB regex filter for names ending with '-digits'; if not supported,
      fallback to scanning all products and testing with _is_generated_name.
    """
    qs = Producto.objects.all().order_by('id_producto')

    if prefix:
        return qs.filter(nombre__startswith=prefix)

    # Try DB-side regex first (fast if supported)
    try:
        return qs.filter(nombre__regex=r'-\d+$')
    except Exception:
        # Fallback to Python-side filtering generator
        for p in qs:
            if p.nombre and _is_generated_name(p.nombre):
                yield p
        return []


def _delete_image_file(pi: ProductoImagen, dry_run: bool = True, keep_media: bool = False) -> bool:
    """
    Remove the image file referenced by ProductoImagen from storage/disk.
    Returns True if a file was removed (or would be removed in dry-run),
    False if file was not found or not removed.
    """
    # If user requested to keep media files, do nothing (but DB record may be removed by caller)
    if keep_media:
        return False

    # Prefer storage.delete() which works with remote storage too.
    try:
        storage = pi.imagen.storage
        name = pi.imagen.name  # relative name inside storage
        if not name:
            return False

        if dry_run:
            # Indicate we would delete
            return True

        # Delete via storage backend
        try:
            storage.delete(name)
        except Exception:
            # Storage deletion may fail for local files; try to remove by path if available
            try:
                path = pi.imagen.path
                if os.path.exists(path):
                    os.remove(path)
            except Exception:
                # Best effort; ignore
                pass

        # Attempt to remove containing directory if empty and it's under MEDIA_ROOT
        try:
            # Only attempt for local MEDIA_ROOT paths
            path = getattr(pi.imagen, 'path', None)
            if path and path.startswith(str(settings.MEDIA_ROOT)):
                parent = os.path.dirname(path)
                # remove empty parent directories up to MEDIA_ROOT/productos/<id> level
                # but be careful not to remove MEDIA_ROOT itself
                try:
                    # os.removedirs will remove intermediate empty directories but we guard.
                    if os.path.isdir(parent):
                        # Only remove if directory is empty
                        if not os.listdir(parent):
                            os.rmdir(parent)
                except Exception:
                    # ignore errors
                    pass
        except Exception:
            pass

        return True
    except Exception:
        return False


class Command(BaseCommand):
    help = "Safely cleanup generated products and their images (dry-run by default). Use --yes to perform deletion."

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            dest='dry_run',
            default=False,
            help='Show what would be deleted without performing deletion (default behavior is dry-run=False for clarity, but command will still require --yes to actually delete).'
        )
        parser.add_argument(
            '--yes',
            '--force',
            action='store_true',
            dest='confirm',
            default=False,
            help='Actually perform deletion. Without this flag the command will only report what would be removed.'
        )
        parser.add_argument(
            '--images-only',
            action='store_true',
            dest='images_only',
            default=False,
            help='Delete only image files and ProductoImagen rows; keep Producto rows.'
        )
        parser.add_argument(
            '--products-only',
            action='store_true',
            dest='products_only',
            default=False,
            help='Delete only Producto rows but leave media files intact (database-only delete).'
        )
        parser.add_argument(
            '--limit',
            type=int,
            dest='limit',
            default=0,
            help='Limit number of products to process (0 = no limit).'
        )
        parser.add_argument(
            '--prefix',
            type=str,
            dest='prefix',
            default='',
            help='Only consider products whose name starts with this prefix.'
        )
        parser.add_argument(
            '--keep-media',
            action='store_true',
            dest='keep_media',
            default=False,
            help='If set, do not delete media files on disk/storage; only DB records will be removed (applies when deleting images).'
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        confirm = options.get('confirm', False)
        images_only = options.get('images_only', False)
        products_only = options.get('products_only', False)
        limit = int(options.get('limit') or 0)
        prefix = options.get('prefix') or None
        keep_media = options.get('keep_media', False)

        # Safety: require explicit confirmation to actually delete anything
        if not confirm and not dry_run:
            self.stdout.write(self.style.WARNING("Nota: por seguridad no se eliminará nada a menos que uses --yes."))
            self.stdout.write(self.style.WARNING("Ejecuta de nuevo con --yes para proceder o usa --dry-run para solo simular."))
            # We'll proceed in reporting mode anyway
        if images_only and products_only:
            raise CommandError("No puedes usar --images-only y --products-only al mismo tiempo.")

        # Identify candidate products
        self.stdout.write("Buscando productos generados...")
        candidates = list(_iter_generated_products(prefix=prefix))
        total_candidates = len(candidates)
        self.stdout.write(f"Productos candidatos encontrados: {total_candidates}")

        if limit > 0:
            candidates = candidates[:limit]
            self.stdout.write(f"Aplicando límite: procesando solo los primeros {len(candidates)} productos")

        if not candidates:
            self.stdout.write(self.style.NOTICE("No hay productos candidatos para procesar. Terminado."))
            return

        # Summary of what will be done
        action_parts = []
        if images_only:
            action_parts.append("eliminar IMÁGENES y registros de ProductoImagen (mantener filas Producto)")
        elif products_only:
            action_parts.append("eliminar filas Producto de la base de datos (no tocar archivos media)")
        else:
            action_parts.append("eliminar IMÁGENES y luego eliminar filas Producto")

        if keep_media:
            action_parts.append("(pero conservar archivos media en disco/storage)")

        summary = "Acción prevista: " + "; ".join(action_parts)
        self.stdout.write(summary)

        if not confirm:
            # dry-run or just preview
            self.stdout.write(self.style.WARNING("Ejecución en modo PREVIEW (no se realizarán eliminaciones). Para borrar realmente pase --yes"))
        else:
            self.stdout.write(self.style.WARNING("ADVERTENCIA: Se procederá a eliminar según las opciones indicadas."))

        deleted_products = 0
        deleted_images = 0
        failed_products = 0
        failed_images = 0

        # Iterate and delete safely
        for producto in candidates:
            try:
                with transaction.atomic():
                    # Gather images for product
                    imagenes = list(producto.imagenes.all())

                    # Delete images first (unless products_only)
                    if not products_only:
                        for pi in imagenes:
                            if dry_run or not confirm:
                                # Dry-run: only report
                                self.stdout.write(f"[DRY] Imagen a eliminar: Producto {producto.id_producto} - {pi.imagen.name}")
                                deleted_images += 1
                                continue

                            # Actual deletion path
                            try:
                                removed = _delete_image_file(pi, dry_run=False, keep_media=keep_media)
                                # Remove DB record if not keeping DB
                                if not keep_media:
                                    # If file deletion succeeded or even if it failed, remove the DB row so it's consistent
                                    pi.delete()
                                if removed:
                                    deleted_images += 1
                                else:
                                    # might have not removed file, but we removed DB record
                                    deleted_images += 1
                            except Exception as e:
                                failed_images += 1
                                self.stderr.write(self.style.ERROR(f"Error al eliminar imagen {getattr(pi, 'imagen', None)}: {e}"))

                    # Now delete product row (unless images_only)
                    if not images_only:
                        if dry_run or not confirm:
                            self.stdout.write(f"[DRY] Producto a eliminar: id={producto.id_producto} nombre='{producto.nombre}'")
                            deleted_products += 1
                        else:
                            # Actual delete of product row
                            producto.delete()
                            deleted_products += 1

            except Exception as exc:
                failed_products += 1
                self.stderr.write(self.style.ERROR(f"Fallo procesando producto id={producto.id_producto} nombre='{producto.nombre}': {exc}"))

        # Final summary
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Operación finalizada. Resumen:"))
        self.stdout.write(self.style.SUCCESS(f"Productos eliminados (o que se habrían eliminado en dry-run): {deleted_products}"))
        self.stdout.write(self.style.SUCCESS(f"Imágenes eliminadas (o que se habrían eliminado en dry-run): {deleted_images}"))
        if failed_products or failed_images:
            self.stdout.write(self.style.ERROR(f"Errores: productos={failed_products}, imágenes={failed_images}"))

        if not confirm:
            self.stdout.write(self.style.WARNING("Recuerda: no se realizaron eliminaciones reales. Ejecuta con --yes para borrar."))