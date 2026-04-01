#!/usr/bin/env python
"""
Fast management command to delete generated Producto records and their associated media files.

Behavior:
- Finds Producto rows by a regex applied to `nombre` (default: names that end with -<digits>).
- Deletes associated ProductoImagen files from storage and the DB.
- Deletes the Producto rows.
- Operates in chunks to handle large numbers quickly without loading all objects at once.
- By default runs in dry-run (preview) mode. Use --yes to actually perform deletions.

Usage examples (from project root where manage.py lives):
- Preview what would be deleted:
    python manage.py delete_generated_fast --limit 100 --pattern "-\\d+$"

- Delete matched items for real:
    python manage.py delete_generated_fast --limit 100 --pattern "-\\d+$" --yes

- Delete only images (leave product rows):
    python manage.py delete_generated_fast --images-only --yes

- Delete only products (leave media on disk):
    python manage.py delete_generated_fast --products-only --yes

Notes:
- This command uses bulk deletes for DB rows (fast). It attempts to remove files via the default storage backend.
- Always run with a dry-run first to confirm the selection.
"""
from __future__ import annotations

import os
import re
from typing import Iterable, List

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db import transaction
from django.db.models import QuerySet

# Use default_storage to support remote storage backends as well as local files
from django.core.files.storage import default_storage

from products.models import Producto, ProductoImagen


def chunked_iterable(iterable: Iterable, size: int) -> Iterable[List]:
    """
    Yield chunks of `size` from `iterable`.
    """
    chunk = []
    for item in iterable:
        chunk.append(item)
        if len(chunk) >= size:
            yield chunk
            chunk = []
    if chunk:
        yield chunk


class Command(BaseCommand):
    help = "Quickly delete generated Producto rows (matched by regex) and their media files. Runs in dry-run by default."

    def add_arguments(self, parser):
        parser.add_argument(
            "--pattern",
            type=str,
            default=r"-\d+$",
            help="Regex pattern to match Producto.nombre (default: '-\\d+$' which matches names ending with -<digits>)",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=0,
            help="Optional: limit number of Producto rows to delete (0 = no limit)",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=200,
            help="How many product IDs to process per chunk (default: 200)",
        )
        parser.add_argument(
            "--images-only",
            action="store_true",
            help="Only remove ProductoImagen files and DB records, keep Producto rows",
        )
        parser.add_argument(
            "--products-only",
            action="store_true",
            help="Only remove Producto rows (do not touch files nor ProductoImagen records)",
        )
        parser.add_argument(
            "--yes",
            "--confirm",
            action="store_true",
            dest="confirm",
            help="Perform deletion. Without this flag the command runs in preview/dry-run mode.",
        )

    def handle(self, *args, **options):
        pattern = options["pattern"]
        limit = int(options["limit"] or 0)
        batch_size = int(options["batch_size"] or 200)
        images_only = options["images_only"]
        products_only = options["products_only"]
        confirm = options["confirm"]

        if images_only and products_only:
            raise CommandError("Cannot use --images-only and --products-only together.")

        # Compile regex to validate user-supplied pattern (this is just to ensure it's valid)
        try:
            re_compiled = re.compile(pattern)
        except re.error as exc:
            raise CommandError(f"Invalid regex pattern: {exc}")

        self.stdout.write(f"Using pattern: {pattern}")
        self.stdout.write(f"Images only: {images_only}, Products only: {products_only}")
        self.stdout.write(f"Batch size: {batch_size}")
        self.stdout.write(f"Limit: {limit or 'no limit'}")
        self.stdout.write("")

        # Build initial queryset of products matching the regex.
        # Use DB-side regex where supported for performance.
        qs: QuerySet = Producto.objects.all().order_by("id_producto")
        try:
            qs = qs.filter(nombre__regex=pattern)
        except Exception:
            # Fallback: load IDs and filter in python if DB backend doesn't support regex.
            self.stdout.write("Database does not support regex filter; falling back to server-side filtering (may be slower).")
            all_qs = Producto.objects.all().order_by("id_producto").values_list("id_producto", "nombre")
            matching_ids = [pid for pid, nombre in all_qs if nombre and re_compiled.search(nombre)]
            qs = Producto.objects.filter(id_producto__in=matching_ids).order_by("id_producto")

        total_matched = qs.count()
        self.stdout.write(f"Matched products: {total_matched}")

        if total_matched == 0:
            self.stdout.write(self.style.SUCCESS("No products matched the given pattern. Exiting."))
            return

        if limit and limit > 0:
            qs = qs[:limit]
            self.stdout.write(f"Applying limit: operating on first {qs.count()} products.")

        # Collect product ids to process (evaluate lazily)
        prod_ids_iterable = list(qs.values_list("id_producto", flat=True))
        total_to_process = len(prod_ids_iterable)
        self.stdout.write(f"Total products to process: {total_to_process}")
        self.stdout.write("IMPORTANT: This command will DELETE data. Run without --yes for a dry-run preview.")
        if not confirm:
            self.stdout.write(self.style.WARNING("Dry-run mode: no deletions will be performed. Use --yes to actually delete."))
        else:
            self.stdout.write(self.style.ERROR("CONFIRMED: The command will perform deletions."))

        # Preview: show the first few products
        preview_count = min(10, total_to_process)
        if preview_count > 0:
            preview_qs = Producto.objects.filter(id_producto__in=prod_ids_iterable[:preview_count]).order_by("id_producto")
            self.stdout.write("Preview of products to be processed:")
            for p in preview_qs:
                self.stdout.write(f" - id={p.id_producto} nombre='{p.nombre}'")
            self.stdout.write("")

        if not confirm:
            # Dry-run only: stop after preview
            self.stdout.write(self.style.SUCCESS("Dry-run complete. No changes made."))
            return

        # Start actual deletion process
        deleted_images = 0
        deleted_image_records = 0
        deleted_products = 0

        # Process in chunks for memory/performance
        for chunk in chunked_iterable(prod_ids_iterable, batch_size):
            # 1) If not products_only: gather image names and delete files and image rows
            if not products_only:
                # Efficiently fetch image field values for products in chunk
                image_names = list(
                    ProductoImagen.objects.filter(producto__id_producto__in=chunk).values_list("imagen", flat=True)
                )

                # Delete files via storage (best-effort)
                for name in image_names:
                    if not name:
                        continue
                    try:
                        # default_storage handles remote and local storage
                        if default_storage.exists(name):
                            default_storage.delete(name)
                            deleted_images += 1
                        else:
                            # If default_storage doesn't know about it, try local path under MEDIA_ROOT
                            local_path = os.path.join(settings.MEDIA_ROOT, name)
                            if os.path.exists(local_path):
                                os.remove(local_path)
                                deleted_images += 1
                    except Exception as exc:
                        # Continue on exceptions; report but do not abort entire run
                        self.stderr.write(f"Warning: could not delete file '{name}': {exc}")

                # Remove ProductoImagen DB rows in bulk
                # This will perform a fast DELETE at DB level
                try:
                    deleted_cnt, _ = ProductoImagen.objects.filter(producto__id_producto__in=chunk).delete()
                    deleted_image_records += deleted_cnt
                except Exception as exc:
                    self.stderr.write(f"Error deleting ProductoImagen rows for products {chunk}: {exc}")

            # 2) If not images_only: delete Producto rows in bulk
            if not images_only:
                try:
                    # Bulk delete; returns (n_deleted, { 'app.Model': n })
                    prod_deleted_cnt, _ = Producto.objects.filter(id_producto__in=chunk).delete()
                    deleted_products += prod_deleted_cnt
                except Exception as exc:
                    self.stderr.write(f"Error deleting Producto rows for ids {chunk}: {exc}")

            # progress update
            self.stdout.write(f"Processed chunk of {len(chunk)} products; totals so far: deleted_images_files={deleted_images}, deleted_image_records={deleted_image_records}, deleted_products={deleted_products}")

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Deletion run complete. Summary:"))
        self.stdout.write(self.style.SUCCESS(f" Image files removed (attempted): {deleted_images}"))
        self.stdout.write(self.style.SUCCESS(f" ProductoImagen DB records deleted (approx): {deleted_image_records}"))
        self.stdout.write(self.style.SUCCESS(f" Producto rows deleted (approx): {deleted_products}"))
        self.stdout.write(self.style.WARNING("If you use remote storage (S3, GCS) confirm that files were actually removed in the storage backend."))