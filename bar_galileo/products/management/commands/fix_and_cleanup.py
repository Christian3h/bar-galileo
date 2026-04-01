#!/usr/bin/env python3
"""
Management command: fix_and_cleanup

- Assign default Categoria / Proveedor / Marca to products missing them.
- Delete products that have NO ProductoImagen associated.
- Remove unreferenced image files under MEDIA_ROOT/productos/ (except the definitive default.jpg).
- Safe by default: runs as a dry-run unless --yes is provided.
- Provides limits and reporting.

Usage examples (run from project root where manage.py lives):
- Preview actions (no changes):
    python manage.py fix_and_cleanup

- Apply defaults only:
    python manage.py fix_and_cleanup --assign-defaults --yes

- Delete products without images (preview):
    python manage.py fix_and_cleanup --delete-no-images --limit 100

- Do everything (assign defaults, delete empty products, remove orphan files):
    python manage.py fix_and_cleanup --assign-defaults --delete-no-images --remove-orphan-files --yes

Options:
  --assign-defaults            Create/assign default Categoria/Proveedor/Marca to products missing them.
  --default-category NAME      Name for default category (default: 'Sin categoría').
  --default-provider NAME      Name for default provider (default: 'Proveedor de prueba').
  --default-brand NAME         Name for default brand (default: 'Marca de prueba').
  --delete-no-images           Delete Producto rows that have no images associated.
  --remove-orphan-files        Remove files under MEDIA_ROOT/productos/ that are not referenced by ProductoImagen.
  --protect-filename NAME      Keep this filename from deletion when removing orphan files (relative to productos/, default: default.jpg).
  --limit N                    Limit number of products to process for destructive actions (0 = no limit).
  --dry-run                    Equivalent to not passing --yes (prints what would happen).
  --yes                        Perform modifications and deletions (required to make changes).
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Iterable, Set, List

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db import transaction

# Import the models from the products app
from products.models import Producto, ProductoImagen, Categoria, Proveedor, Marca


class Command(BaseCommand):
    help = "Assign defaults, delete products without images, and remove orphan image files (dry-run by default)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--assign-defaults",
            action="store_true",
            dest="assign_defaults",
            help="Create and assign default Categoria/Proveedor/Marca for products missing them.",
        )
        parser.add_argument(
            "--default-category",
            dest="default_category",
            default="Sin categoría",
            help="Name for default Categoria (default: 'Sin categoría').",
        )
        parser.add_argument(
            "--default-provider",
            dest="default_provider",
            default="Proveedor de prueba",
            help="Name for default Proveedor (default: 'Proveedor de prueba').",
        )
        parser.add_argument(
            "--default-brand",
            dest="default_brand",
            default="Marca de prueba",
            help="Name for default Marca (default: 'Marca de prueba').",
        )
        parser.add_argument(
            "--delete-no-images",
            action="store_true",
            dest="delete_no_images",
            help="Delete Producto rows that have no related ProductoImagen.",
        )
        parser.add_argument(
            "--remove-orphan-files",
            action="store_true",
            dest="remove_orphan_files",
            help="Remove files in MEDIA_ROOT/productos/ that are not referenced by any ProductoImagen.",
        )
        parser.add_argument(
            "--protect-filename",
            dest="protect_filename",
            default="default.jpg",
            help="Filename under productos/ to protect from orphan deletion (default: default.jpg).",
        )
        parser.add_argument(
            "--limit",
            dest="limit",
            type=int,
            default=0,
            help="Limit number of products to process for destructive actions (0 = no limit).",
        )
        parser.add_argument(
            "--yes",
            action="store_true",
            dest="confirm",
            help="Confirm and perform destructive operations. Without this flag the command runs in preview mode.",
        )

    def _media_productos_dir(self) -> Path:
        media_root = getattr(settings, "MEDIA_ROOT", None)
        if not media_root:
            raise CommandError("MEDIA_ROOT is not configured in settings.")
        return Path(media_root) / "productos"

    def _gather_referenced_paths(self) -> Set[str]:
        """
        Return the set of relative paths (relative to MEDIA_ROOT) referenced by ProductoImagen.imagen.
        Example entries: 'productos/123/default_123.webp'
        """
        referenced = set()
        for name in ProductoImagen.objects.values_list("imagen", flat=True):
            if name:
                # Normalize to posix style path for comparison
                referenced.add(str(Path(name)))
        return referenced

    def _iter_orphan_files(self, media_productos: Path, referenced_relpaths: Set[str], protect: str) -> Iterable[Path]:
        """
        Iterate files under media_productos that are not referenced. `referenced_relpaths`
        contains relative paths like 'productos/123/img.webp' (relative to MEDIA_ROOT).
        We compare using Path(relative).name and full relative path.
        """
        # Build set of protected full-relative paths (e.g. 'productos/default.jpg')
        protected_name = protect
        protected_relpath = f"productos/{protect}"
        for root, dirs, files in os.walk(media_productos):
            for fname in files:
                full_path = Path(root) / fname
                # Build relative path to MEDIA_ROOT (posix)
                rel = os.path.relpath(str(full_path), settings.MEDIA_ROOT)
                rel_posix = str(Path(rel).as_posix())
                # Skip protected
                if fname == protected_name or rel_posix == protected_relpath:
                    continue
                # If not referenced, yield
                if rel_posix not in referenced_relpaths:
                    yield full_path

    def handle(self, *args, **options):
        assign_defaults = options.get("assign_defaults", False)
        default_category_name = options.get("default_category")
        default_provider_name = options.get("default_provider")
        default_brand_name = options.get("default_brand")
        delete_no_images = options.get("delete_no_images", False)
        remove_orphan_files = options.get("remove_orphan_files", False)
        protect_filename = options.get("protect_filename", "default.jpg")
        limit = int(options.get("limit") or 0)
        confirm = options.get("confirm", False)

        dry_run = not confirm

        if not (assign_defaults or delete_no_images or remove_orphan_files):
            self.stdout.write(self.style.NOTICE("No action requested. Use --assign-defaults, --delete-no-images and/or --remove-orphan-files."))
            return

        # Show high-level plan
        self.stdout.write("Plan:")
        if assign_defaults:
            self.stdout.write(f" - Assign default Categoria/Proveedor/Marca (category='{default_category_name}', provider='{default_provider_name}', brand='{default_brand_name}')")
        if delete_no_images:
            self.stdout.write(" - Delete Producto rows that have no images associated.")
        if remove_orphan_files:
            self.stdout.write(f" - Remove files under MEDIA_ROOT/productos/ that are not referenced (protect: {protect_filename})")
        self.stdout.write(f"Dry-run: {'YES' if dry_run else 'NO (changes will be applied)'}")
        if limit > 0:
            self.stdout.write(f"Limit: {limit} items for destructive ops")

        # Step A: assign defaults
        default_category = default_provider = default_brand = None
        if assign_defaults:
            # Create or get defaults (do not create multiple duplicates)
            if dry_run:
                self.stdout.write(self.style.NOTICE("DRY RUN: would ensure default Categoria/Proveedor/Marca exist."))
            else:
                default_category, _ = Categoria.objects.get_or_create(nombre_categoria=default_category_name)
                default_provider, _ = Proveedor.objects.get_or_create(nombre=default_provider_name, defaults={"contacto": default_provider_name, "direccion": ""})
                default_brand, _ = Marca.objects.get_or_create(marca=default_brand_name)
                self.stdout.write(self.style.SUCCESS(f"Ensured defaults: Categoria(id={getattr(default_category, 'id_categoria', None)}), Proveedor(id={getattr(default_provider, 'id_proveedor', None)}), Marca(id={getattr(default_brand, 'id_marca', None)})"))

            # Now update products missing those fields
            # Build queryset of products missing any of the three fields
            missing_qs = Producto.objects.filter(
                # Using OR: missing category OR missing provider OR missing brand
            ).order_by("id_producto")
            # Construct filter dynamically: Django doesn't support OR easily here without Q import,
            # but we can fetch all and filter in Python since scale is manageable.
            all_products = Producto.objects.all().order_by("id_producto")
            to_update = []
            for p in all_products:
                needs = False
                if p.id_categoria is None or (hasattr(p.id_categoria, "nombre_categoria") and not p.id_categoria.nombre_categoria):
                    needs = True
                if p.id_proveedor is None:
                    needs = True
                if p.id_marca is None:
                    needs = True
                if needs:
                    to_update.append(p)
            total_missing = len(to_update)
            self.stdout.write(f"Products missing category/provider/brand: {total_missing}")

            if total_missing:
                if dry_run:
                    self.stdout.write(self.style.WARNING("DRY RUN: would assign default Categoria/Proveedor/Marca to the following product IDs (showing up to 50):"))
                    self.stdout.write(", ".join(str(p.id_producto) for p in to_update[:50]))
                else:
                    # Perform updates (respect limit)
                    processed = 0
                    for p in to_update:
                        if limit and processed >= limit:
                            break
                        updated = False
                        if p.id_categoria is None or (hasattr(p.id_categoria, "nombre_categoria") and not p.id_categoria.nombre_categoria):
                            p.id_categoria = default_category
                            updated = True
                        if p.id_proveedor is None:
                            p.id_proveedor = default_provider
                            updated = True
                        if p.id_marca is None:
                            p.id_marca = default_brand
                            updated = True
                        if updated:
                            p.save(update_fields=["id_categoria", "id_proveedor", "id_marca"])
                        processed += 1
                    self.stdout.write(self.style.SUCCESS(f"Assigned defaults to {processed} products."))

        # Step B: delete products without images
        deleted_products_count = 0
        if delete_no_images:
            # Products with no related images:
            qs_no_images = Producto.objects.filter(imagenes__isnull=True).order_by("id_producto")
            # Note: filter(imagenes__isnull=True) returns products with no related ProductoImagen
            total_no_images = qs_no_images.count()
            self.stdout.write(f"Products without images found: {total_no_images}")

            if total_no_images:
                # Show preview (first 50)
                preview_ids = list(qs_no_images.values_list("id_producto", flat=True)[:50])
                self.stdout.write("Sample product IDs without images (first 50):")
                self.stdout.write(", ".join(str(x) for x in preview_ids))

                if dry_run:
                    self.stdout.write(self.style.WARNING("DRY RUN: would delete these products (or up to --limit if provided)."))
                else:
                    # Delete respecting limit
                    to_delete_qs = qs_no_images
                    if limit:
                        ids = list(to_delete_qs.values_list("id_producto", flat=True)[:limit])
                        to_delete_qs = Producto.objects.filter(id_producto__in=ids)
                    # Delete in a transaction
                    with transaction.atomic():
                        deleted_count, _ = to_delete_qs.delete()
                        deleted_products_count = deleted_count
                    self.stdout.write(self.style.SUCCESS(f"Deleted {deleted_products_count} products that had no images."))

        # Step C: remove orphan files under MEDIA_ROOT/productos/
        removed_files_count = 0
        if remove_orphan_files:
            media_productos = self._media_productos_dir()
            if not media_productos.exists():
                self.stdout.write(self.style.WARNING(f"No media/productos directory found at {media_productos}. Nothing to remove."))
            else:
                referenced = self._gather_referenced_paths()
                # Normalize referenced paths to posix relative paths (productos/...)
                referenced_posix = set(str(Path(p).as_posix()) for p in referenced)
                self.stdout.write(f"Referenced image paths in DB: {len(referenced_posix)}")

                # Iterate through files and delete orphan ones
                orphans = list(self._iter_orphan_files(media_productos, referenced_posix, protect_filename))
                self.stdout.write(f"Orphan files detected: {len(orphans)} (excluding protected '{protect_filename}')")
                if len(orphans) > 0:
                    if dry_run:
                        self.stdout.write(self.style.WARNING("DRY RUN: the following orphan files would be removed (first 100 listed):"))
                        for f in orphans[:100]:
                            self.stdout.write(str(f))
                    else:
                        removed = 0
                        for fpath in orphans:
                            try:
                                if fpath.exists():
                                    fpath.unlink()
                                    removed += 1
                            except Exception as exc:
                                self.stderr.write(self.style.ERROR(f"Failed to remove {fpath}: {exc}"))
                        # Attempt to remove any empty directories under productos
                        for root, dirs, files in os.walk(media_productos, topdown=False):
                            try:
                                if not os.listdir(root):
                                    os.rmdir(root)
                            except Exception:
                                # ignore
                                pass
                        removed_files_count = removed
                        self.stdout.write(self.style.SUCCESS(f"Removed {removed_files_count} orphan files."))

        # Final summary
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("fix_and_cleanup summary:"))
        if assign_defaults:
            self.stdout.write(self.style.SUCCESS(f" - Defaults assignment: {'DRY RUN' if dry_run else 'APPLIED'}"))
        if delete_no_images:
            self.stdout.write(self.style.SUCCESS(f" - Products deleted (no images): {deleted_products_count if not dry_run else 'DRY RUN (no changes)'}"))
        if remove_orphan_files:
            self.stdout.write(self.style.SUCCESS(f" - Orphan files removed: {removed_files_count if not dry_run else 'DRY RUN (no changes)'}"))

        self.stdout.write(self.style.NOTICE("Done."))