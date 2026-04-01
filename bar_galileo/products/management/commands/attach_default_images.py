from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.conf import settings
import os

from products.models import Producto, ProductoImagen, procesar_y_guardar_imagen


class Command(BaseCommand):
    help = (
        "Attach copies of a default image to products. "
        "By default it will add one copy of the default image to each product that has no images. "
        "You can force re-attachment with --force and create multiple copies per product with --copies."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--default',
            dest='default_relpath',
            default='productos/default.jpg',
            help="Relative path inside MEDIA_ROOT for the source default image (default: 'productos/default.jpg')"
        )
        parser.add_argument(
            '--force',
            action='store_true',
            dest='force',
            help="If set, will attach images even to products that already have images."
        )
        parser.add_argument(
            '--copies',
            dest='copies',
            type=int,
            default=1,
            help="Number of copies to attach per product (default: 1). Each copy will get a unique filename."
        )
        parser.add_argument(
            '--limit',
            dest='limit',
            type=int,
            default=0,
            help="Optional: limit number of products processed (for testing). 0 means no limit."
        )

    def handle(self, *args, **options):
        default_rel = options['default_relpath']
        force = options['force']
        copies = max(1, options['copies'] or 1)
        limit = options['limit'] or 0

        media_root = getattr(settings, 'MEDIA_ROOT', None)
        if not media_root:
            raise CommandError("MEDIA_ROOT is not configured in settings.")

        source_path = os.path.join(media_root, default_rel)
        if not os.path.exists(source_path):
            raise CommandError(f"Default source image not found at: {source_path}")

        productos_qs = Producto.objects.all().order_by('id_producto')
        total = productos_qs.count()
        if limit and limit > 0:
            productos_qs = productos_qs[:limit]

        processed = 0
        attached = 0
        skipped = 0
        errors = 0

        self.stdout.write(self.style.NOTICE(f"Starting attachment process. Source: {source_path}"))
        self.stdout.write(self.style.NOTICE(f"Total products to consider: {total}{' (limited to ' + str(limit) + ')' if limit else ''}"))
        self.stdout.write(self.style.NOTICE(f"Copies per product: {copies}"))
        self.stdout.write(self.style.NOTICE(f"Force attach: {'YES' if force else 'NO'}"))
        self.stdout.write("")

        for producto in productos_qs:
            processed += 1
            try:
                has_images = producto.imagenes.exists()
                if has_images and not force:
                    skipped += 1
                    self.stdout.write(self.style.WARNING(f"[SKIP] Producto {producto.id_producto} - '{producto.nombre}' already has images."))
                    continue

                # For safety and idempotency, if force is True we will still create new copies
                # (you can later remove duplicates or extend logic to delete existing images first)
                created_count = 0

                # Wrap creation of a product's images in a transaction so partial writes per-product are rolled back
                with transaction.atomic():
                    for i in range(1, copies + 1):
                        # Use a per-product unique basename so files are not reused across products.
                        nombre_base = f"default_{producto.id_producto}"
                        if copies > 1:
                            nombre_base = f"{nombre_base}_{i}"

                        # Open the source file fresh for each conversion to avoid file-pointer issues
                        with open(source_path, 'rb') as src_file:
                            # procesar_y_guardar_imagen will convert to webp and store under MEDIA_ROOT/productos/{id}/
                            ruta_relativa = procesar_y_guardar_imagen(src_file, producto.id_producto, nombre_base)

                        # Create ProductoImagen pointing to the saved relative path
                        pi = ProductoImagen(producto=producto)
                        # Assign the relative path (relative to MEDIA_ROOT) to the ImageField name
                        pi.imagen.name = ruta_relativa
                        pi.save()
                        created_count += 1

                attached += created_count
                self.stdout.write(self.style.SUCCESS(f"[OK] Producto {producto.id_producto} - '{producto.nombre}': attached {created_count} image(s)."))

            except Exception as exc:
                errors += 1
                self.stderr.write(self.style.ERROR(f"[ERROR] Producto {producto.id_producto} - '{producto.nombre}': {exc}"))

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Attachment run completed."))
        self.stdout.write(self.style.SUCCESS(f"Processed: {processed} products"))
        self.stdout.write(self.style.SUCCESS(f"Attached images: {attached}"))
        self.stdout.write(self.style.WARNING(f"Skipped (had images and --force not set): {skipped}"))
        self.stdout.write(self.style.ERROR(f"Errors: {errors}"))