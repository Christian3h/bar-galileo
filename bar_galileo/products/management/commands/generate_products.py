from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from decimal import Decimal, ROUND_HALF_UP
from faker import Faker
import random
import time

from products.models import Producto


def to_decimal(value):
    """Round a float to 2 decimal places and return Decimal."""
    return Decimal(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


class Command(BaseCommand):
    help = "Generate fake Producto records using Faker. Does not attach images."

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=1000,
            help='Number of products to create (default: 1000).'
        )
        parser.add_argument(
            '--start',
            type=int,
            default=1,
            help='Starting index used to make product names unique (default: 1).'
        )
        parser.add_argument(
            '--batch',
            type=int,
            default=100,
            help='How many products to create between progress updates (default: 100).'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Do not actually save to DB; just show what would be created.'
        )
        parser.add_argument(
            '--sleep',
            type=float,
            default=0.0,
            help='Optional delay in seconds between each created product (useful for watching progress).'
        )

    def handle(self, *args, **options):
        count = options['count']
        start = options['start']
        batch = max(1, options['batch'])
        dry_run = options['dry_run']
        sleep = float(options.get('sleep') or 0.0)

        if count <= 0:
            raise CommandError('--count must be greater than 0')

        fake = Faker()
        created = 0
        failed = 0
        start_time = time.time()

        self.stdout.write(self.style.NOTICE(f"Generating {count} products (dry-run={dry_run})..."))

        # Use a DB transaction for the whole run to allow easy rollback if needed.
        # If dry-run, we will not enter transaction that creates objects.
        try:
            if dry_run:
                # Simulate creation without touching DB
                for i in range(count):
                    idx = start + i
                    nombre = f"{fake.word()}-{idx}"
                    precio_compra = to_decimal(random.uniform(1.0, 80.0))
                    # Ensure precio_venta > precio_compra
                    precio_venta = to_decimal(float(precio_compra) + random.uniform(0.5, 50.0))
                    stock = random.randint(0, 200)
                    descripcion = fake.sentence(nb_words=12)

                    if (i + 1) % batch == 0 or (i + 1) == count:
                        self.stdout.write(f"[DRY] Prepared {i+1}/{count}: {nombre} — compra={precio_compra} venta={precio_venta} stock={stock}")
                    if sleep:
                        time.sleep(sleep)
                self.stdout.write(self.style.SUCCESS("Dry run finished. No objects were created."))
                return

            # Real creation path
            with transaction.atomic():
                for i in range(count):
                    idx = start + i
                    # Generate a reasonably unique name by appending the index.
                    nombre = f"{fake.word()}-{idx}"

                    # Generate prices guaranteeing precio_venta > precio_compra to satisfy model.clean()
                    precio_compra = to_decimal(random.uniform(1.0, 80.0))
                    precio_venta = to_decimal(float(precio_compra) + random.uniform(0.5, 50.0))

                    stock = random.randint(0, 200)
                    descripcion = fake.sentence(nb_words=12)

                    try:
                        Producto.objects.create(
                            nombre=nombre,
                            precio_compra=precio_compra,
                            precio_venta=precio_venta,
                            stock=stock,
                            descripcion=descripcion,
                            activo=True,
                            id_categoria=None,
                            id_proveedor=None,
                            id_marca=None,
                        )
                        created += 1
                    except Exception as exc:
                        failed += 1
                        self.stderr.write(self.style.ERROR(f"[ERROR] [{i+1}/{count}] {nombre}: {exc}"))

                    # Progress reporting
                    if (i + 1) % batch == 0 or (i + 1) == count:
                        elapsed = time.time() - start_time
                        self.stdout.write(f"[PROGRESS] Created {created} / {i+1} (failed: {failed}) — elapsed: {elapsed:.1f}s")

                    if sleep:
                        time.sleep(sleep)

        except Exception as exc:
            raise CommandError(f"Unexpected error during generation: {exc}")

        total_time = time.time() - start_time
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(f"Finished: created={created} failed={failed} total_requested={count}"))
        self.stdout.write(self.style.SUCCESS(f"Elapsed time: {total_time:.1f}s"))