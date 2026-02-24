"""
Comando de Django para llenar la base de datos con datos falsos.
Incluye productos reales de licor vendidos en Colombia.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta
import random

# Importar modelos
from products.models import Categoria, Marca, Proveedor, Producto, Stock
from tables.models import Mesa, Pedido, PedidoItem, Factura
from expenses.models import ExpenseCategory, Expense
from facturacion.models import FacturaOriginal
from nominas.models import Empleado, Pago, Bonificacion
from roles.models import Role, Module, Action, RolePermission, UserProfile
from reportes.models import Reporte


class Command(BaseCommand):
    help = 'Vacía y llena la base de datos con datos falsos para pruebas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-clear',
            action='store_true',
            help='No vaciar datos existentes antes de agregar nuevos',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('🚀 Iniciando generación de datos falsos...'))

        # Vaciar datos existentes si no se especifica --no-clear
        if not options['no_clear']:
            self.vaciar_datos()

        # Llenar con datos falsos
        self.crear_roles_y_permisos()
        self.crear_usuarios()
        self.crear_categorias()
        self.crear_marcas()
        self.crear_proveedores()
        self.crear_productos_licor()
        self.crear_mesas()
        self.crear_empleados()
        self.crear_expense_categories()
        self.crear_gastos()
        self.crear_pedidos_y_facturas()
        self.crear_nominas()
        self.crear_reportes()

        self.stdout.write(self.style.SUCCESS('✅ Datos falsos generados exitosamente!'))

    def vaciar_datos(self):
        """Vacía todas las tablas de datos (excepto superusuarios)"""
        self.stdout.write(self.style.WARNING('🗑️  Vaciando datos existentes...'))

        try:
            # Orden de borrado para respetar foreign keys
            Reporte.objects.all().delete()
            Bonificacion.objects.all().delete()
            Pago.objects.all().delete()
            Empleado.objects.all().delete()
            Expense.objects.all().delete()
            ExpenseCategory.objects.all().delete()

            # Facturación
            FacturaOriginal.objects.all().delete()
            Factura.objects.all().delete()

            # Pedidos
            PedidoItem.objects.all().delete()
            Pedido.objects.all().delete()
            Mesa.objects.all().delete()

            # Productos y relaciones
            Stock.objects.all().delete()
            Producto.objects.all().delete()
            Proveedor.objects.all().delete()
            Marca.objects.all().delete()
            Categoria.objects.all().delete()

            # Usuarios y permisos (excepto superusuarios)
            # Eliminar solo UserProfiles que no pertenezcan a superusuarios
            UserProfile.objects.exclude(user__is_superuser=True).delete()
            # Eliminar usuarios no superusuarios que no tengan empleado
            User.objects.filter(is_superuser=False).exclude(empleado__isnull=False).delete()
            RolePermission.objects.all().delete()
            # No eliminar todos los roles, solo los que no tienen usuarios superusuarios
            # Role.objects.all().delete()
            # Action.objects.all().delete()
            # Module.objects.all().delete()

            self.stdout.write(self.style.SUCCESS('   ✓ Datos vaciados'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'   ⚠ Advertencia al vaciar datos: {str(e)}'))
            self.stdout.write(self.style.WARNING('   Continuando con la creación de datos...'))

    def crear_roles_y_permisos(self):
        """Crear roles, módulos y acciones básicos"""
        self.stdout.write('📋 Creando roles y permisos...')

        # Crear acciones
        acciones = ['ver', 'crear', 'editar', 'eliminar']
        for nombre in acciones:
            Action.objects.get_or_create(nombre=nombre)

        # Crear módulos
        modulos = [
            'products', 'tables', 'users', 'providers', 'brands',
            'roles', 'categories', 'dashboard', 'expenses', 'nominas',
            'backups', 'facturacion', 'reportes', 'notifications'
        ]
        for nombre in modulos:
            Module.objects.get_or_create(nombre=nombre)

        # Crear roles
        roles_data = [
            {'nombre': 'Administrador', 'descripcion': 'Acceso total al sistema'},
            {'nombre': 'Gerente', 'descripcion': 'Gestión de empleados y reportes'},
            {'nombre': 'Empleado', 'descripcion': 'Acceso básico a mesas y pedidos'},
            {'nombre': 'Mesero', 'descripcion': 'Gestión de mesas y pedidos'},
            {'nombre': 'Usuario', 'descripcion': 'Solo lectura'},
        ]

        for data in roles_data:
            Role.objects.get_or_create(nombre=data['nombre'], defaults={'descripcion': data['descripcion']})

        self.stdout.write(self.style.SUCCESS('   ✓ Roles y permisos creados'))

    def crear_usuarios(self):
        """Crear usuarios de prueba"""
        self.stdout.write('👥 Creando usuarios...')

        usuarios_data = [
            {'username': 'admin', 'email': 'admin@bargalileo.com', 'first_name': 'Admin', 'last_name': 'Sistema', 'rol': 'Administrador'},
            {'username': 'gerente', 'email': 'gerente@bargalileo.com', 'first_name': 'María', 'last_name': 'González', 'rol': 'Gerente'},
            {'username': 'mesero1', 'email': 'mesero1@bargalileo.com', 'first_name': 'Carlos', 'last_name': 'Ruiz', 'rol': 'Mesero'},
            {'username': 'mesero2', 'email': 'mesero2@bargalileo.com', 'first_name': 'Ana', 'last_name': 'López', 'rol': 'Mesero'},
            {'username': 'empleado1', 'email': 'empleado1@bargalileo.com', 'first_name': 'Juan', 'last_name': 'Martínez', 'rol': 'Empleado'},
        ]

        for data in usuarios_data:
            rol_nombre = data.pop('rol')
            is_admin = data['username'] == 'admin'

            user, created = User.objects.get_or_create(
                username=data['username'],
                defaults={
                    **data,
                    'is_staff': True,
                    'is_superuser': is_admin  # Admin es superusuario
                }
            )
            if created:
                user.set_password('password123')
                user.save()

                # Asignar rol
                rol = Role.objects.filter(nombre=rol_nombre).first()
                if rol:
                    UserProfile.objects.create(user=user, rol=rol)

        self.stdout.write(self.style.SUCCESS(f'   ✓ {len(usuarios_data)} usuarios creados'))

    def crear_categorias(self):
        """Crear categorías de productos"""
        self.stdout.write('🏷️  Creando categorías...')

        categorias = [
            {'nombre': 'Aguardiente', 'descripcion': 'Bebidas destiladas anisadas típicas de Colombia'},
            {'nombre': 'Ron', 'descripcion': 'Rones nacionales e importados'},
            {'nombre': 'Whisky', 'descripcion': 'Whiskys escoceses, irlandeses y americanos'},
            {'nombre': 'Vodka', 'descripcion': 'Vodkas nacionales e importados'},
            {'nombre': 'Cerveza', 'descripcion': 'Cervezas nacionales y artesanales'},
            {'nombre': 'Vino', 'descripcion': 'Vinos tintos, blancos y rosados'},
            {'nombre': 'Tequila', 'descripcion': 'Tequilas y mezcales'},
            {'nombre': 'Ginebra', 'descripcion': 'Ginebras premium y clásicas'},
            {'nombre': 'Licores', 'descripcion': 'Cremas, amaretto, baileys, etc'},
            {'nombre': 'Brandy', 'descripcion': 'Brandys y cognacs'},
        ]

        for cat_data in categorias:
            Categoria.objects.get_or_create(
                nombre_categoria=cat_data['nombre'],
                defaults={'descripcion': cat_data['descripcion']}
            )

        self.stdout.write(self.style.SUCCESS(f'   ✓ {len(categorias)} categorías creadas'))

    def crear_marcas(self):
        """Crear marcas de productos de licor colombianos"""
        self.stdout.write('🏭 Creando marcas...')

        marcas = [
            # Aguardientes
            {'nombre': 'Antioqueño', 'descripcion': 'Aguardiente líder en Colombia'},
            {'nombre': 'Nectar', 'descripcion': 'Aguardiente tradicional del Valle'},
            {'nombre': 'Cristal', 'descripcion': 'Aguardiente de Caldas'},
            {'nombre': 'Tapa Roja', 'descripcion': 'Aguardiente clásico'},

            # Rones
            {'nombre': 'Ron Viejo de Caldas', 'descripcion': 'Ron colombiano premium'},
            {'nombre': 'Medellín Añejo', 'descripcion': 'Ron de Antioquia'},
            {'nombre': 'Ron Tres Esquinas', 'descripcion': 'Ron tradicional'},
            {'nombre': 'Bacardí', 'descripcion': 'Ron internacional'},

            # Cervezas
            {'nombre': 'Águila', 'descripcion': 'Cerveza líder en Colombia'},
            {'nombre': 'Poker', 'descripcion': 'Cerveza tradicional'},
            {'nombre': 'Club Colombia', 'descripcion': 'Cerveza premium'},
            {'nombre': 'Corona', 'descripcion': 'Cerveza mexicana'},

            # Whiskys
            {'nombre': 'Buchanan\'s', 'descripcion': 'Whisky escocés'},
            {'nombre': 'Old Parr', 'descripcion': 'Whisky escocés premium'},
            {'nombre': 'Johnnie Walker', 'descripcion': 'Whisky escocés icónico'},

            # Otros
            {'nombre': 'Absolut', 'descripcion': 'Vodka sueco'},
            {'nombre': 'Smirnoff', 'descripcion': 'Vodka clásico'},
            {'nombre': 'Gato Negro', 'descripcion': 'Vinos chilenos'},
            {'nombre': 'Jose Cuervo', 'descripcion': 'Tequila mexicano'},
        ]

        for marca_data in marcas:
            Marca.objects.get_or_create(
                marca=marca_data['nombre'],
                defaults={'descripcion': marca_data['descripcion']}
            )

        self.stdout.write(self.style.SUCCESS(f'   ✓ {len(marcas)} marcas creadas'))

    def crear_proveedores(self):
        """Crear proveedores"""
        self.stdout.write('🚚 Creando proveedores...')

        proveedores = [
            {
                'nombre': 'Licores del Valle S.A.S',
                'contacto': 'Roberto Pérez',
                'telefono': 3001234567,
                'direccion': 'Calle 15 #25-30, Cali, Valle del Cauca'
            },
            {
                'nombre': 'Distribuidora Antioqueña',
                'contacto': 'Claudia Gómez',
                'telefono': 3009876543,
                'direccion': 'Carrera 45 #70-25, Medellín, Antioquia'
            },
            {
                'nombre': 'Importadora Nacional de Licores',
                'contacto': 'Luis Hernández',
                'telefono': 3157894561,
                'direccion': 'Av. El Dorado #68-40, Bogotá D.C.'
            },
            {
                'nombre': 'Cervezas y Licores La Central',
                'contacto': 'Diana Morales',
                'telefono': 3123456789,
                'direccion': 'Carrera 7 #32-16, Bogotá D.C.'
            },
            {
                'nombre': 'Destilería Andina',
                'contacto': 'Jorge Castro',
                'telefono': 3201122334,
                'direccion': 'Km 5 Vía Manizales, Caldas'
            },
            {
                'nombre': 'Licorería Premium Ltda',
                'contacto': 'Sandra Vargas',
                'telefono': 3184567890,
                'direccion': 'Calle 100 #18A-30, Bogotá D.C.'
            },
            {
                'nombre': 'Distribuciones El Barril',
                'contacto': 'Miguel Ángel Rojas',
                'telefono': 3167890123,
                'direccion': 'Carrera 50 #12-34, Barranquilla, Atlántico'
            },
            {
                'nombre': 'Vinos y Licores Importados',
                'contacto': 'Patricia Reyes',
                'telefono': 3145678901,
                'direccion': 'Calle 85 #15-25, Bogotá D.C.'
            },
        ]

        for prov_data in proveedores:
            Proveedor.objects.get_or_create(
                nombre=prov_data['nombre'],
                defaults=prov_data
            )

        self.stdout.write(self.style.SUCCESS(f'   ✓ {len(proveedores)} proveedores creados'))

    def crear_productos_licor(self):
        """Crear productos reales de licor vendidos en Colombia"""
        self.stdout.write('🍺 Creando productos de licor colombianos...')

        # Obtener categorías, marcas y proveedores
        categorias = {c.nombre_categoria: c for c in Categoria.objects.all()}
        marcas = {m.marca: m for m in Marca.objects.all()}
        proveedores = list(Proveedor.objects.all())

        productos = [
            # Aguardientes (8 productos)
            {
                'nombre': 'Aguardiente Antioqueño Sin Azúcar',
                'categoria': 'Aguardiente',
                'marca': 'Antioqueño',
                'precio_compra': 28000,
                'precio_venta': 45000,
                'stock': random.randint(30, 100),
                'descripcion': 'Aguardiente sin azúcar de 29 grados, 750ml'
            },
            {
                'nombre': 'Aguardiente Antioqueño Verde',
                'categoria': 'Aguardiente',
                'marca': 'Antioqueño',
                'precio_compra': 32000,
                'precio_venta': 50000,
                'stock': random.randint(20, 80),
                'descripcion': 'Aguardiente tradicional de 29 grados, 750ml'
            },
            {
                'nombre': 'Aguardiente Nectar Club',
                'categoria': 'Aguardiente',
                'marca': 'Nectar',
                'precio_compra': 30000,
                'precio_venta': 48000,
                'stock': random.randint(25, 90),
                'descripcion': 'Aguardiente del Valle del Cauca, 750ml'
            },
            {
                'nombre': 'Aguardiente Cristal',
                'categoria': 'Aguardiente',
                'marca': 'Cristal',
                'precio_compra': 26000,
                'precio_venta': 42000,
                'stock': random.randint(30, 85),
                'descripcion': 'Aguardiente de Caldas, 750ml'
            },
            {
                'nombre': 'Aguardiente Tapa Roja',
                'categoria': 'Aguardiente',
                'marca': 'Tapa Roja',
                'precio_compra': 24000,
                'precio_venta': 39000,
                'stock': random.randint(35, 95),
                'descripcion': 'Aguardiente clásico de 29 grados, 750ml'
            },
            {
                'nombre': 'Aguardiente Antioqueño Azul',
                'categoria': 'Aguardiente',
                'marca': 'Antioqueño',
                'precio_compra': 35000,
                'precio_venta': 55000,
                'stock': random.randint(15, 60),
                'descripcion': 'Aguardiente premium azul, 750ml'
            },
            {
                'nombre': 'Aguardiente Nectar Rojo',
                'categoria': 'Aguardiente',
                'marca': 'Nectar',
                'precio_compra': 28000,
                'precio_venta': 46000,
                'stock': random.randint(20, 75),
                'descripcion': 'Aguardiente rojo tradicional, 750ml'
            },
            {
                'nombre': 'Aguardiente Nectar Limonada',
                'categoria': 'Aguardiente',
                'marca': 'Nectar',
                'precio_compra': 30000,
                'precio_venta': 48000,
                'stock': random.randint(18, 70),
                'descripcion': 'Aguardiente con sabor a limonada, 750ml'
            },

            # Rones (6 productos)
            {
                'nombre': 'Ron Viejo de Caldas 8 Años',
                'categoria': 'Ron',
                'marca': 'Ron Viejo de Caldas',
                'precio_compra': 45000,
                'precio_venta': 72000,
                'stock': random.randint(15, 50),
                'descripcion': 'Ron añejo colombiano 8 años, 750ml'
            },
            {
                'nombre': 'Ron Viejo de Caldas 3 Años',
                'categoria': 'Ron',
                'marca': 'Ron Viejo de Caldas',
                'precio_compra': 32000,
                'precio_venta': 52000,
                'stock': random.randint(20, 65),
                'descripcion': 'Ron añejo colombiano 3 años, 750ml'
            },
            {
                'nombre': 'Ron Medellín Añejo',
                'categoria': 'Ron',
                'marca': 'Medellín Añejo',
                'precio_compra': 38000,
                'precio_venta': 60000,
                'stock': random.randint(18, 55),
                'descripcion': 'Ron añejo de Antioquia, 750ml'
            },
            {
                'nombre': 'Ron Tres Esquinas Extra Añejo',
                'categoria': 'Ron',
                'marca': 'Ron Tres Esquinas',
                'precio_compra': 42000,
                'precio_venta': 68000,
                'stock': random.randint(12, 45),
                'descripcion': 'Ron extra añejo colombiano, 750ml'
            },
            {
                'nombre': 'Bacardí Carta Blanca',
                'categoria': 'Ron',
                'marca': 'Bacardí',
                'precio_compra': 48000,
                'precio_venta': 75000,
                'stock': random.randint(25, 70),
                'descripcion': 'Ron blanco internacional, 750ml'
            },
            {
                'nombre': 'Bacardí Carta Oro',
                'categoria': 'Ron',
                'marca': 'Bacardí',
                'precio_compra': 50000,
                'precio_venta': 78000,
                'stock': random.randint(20, 60),
                'descripcion': 'Ron dorado internacional, 750ml'
            },

            # Cervezas (7 productos)
            {
                'nombre': 'Cerveza Águila Original 330ml',
                'categoria': 'Cerveza',
                'marca': 'Águila',
                'precio_compra': 2000,
                'precio_venta': 3500,
                'stock': random.randint(100, 300),
                'descripcion': 'Cerveza rubia colombiana'
            },
            {
                'nombre': 'Cerveza Poker Roja 330ml',
                'categoria': 'Cerveza',
                'marca': 'Poker',
                'precio_compra': 2100,
                'precio_venta': 3600,
                'stock': random.randint(90, 280),
                'descripcion': 'Cerveza roja tradicional'
            },
            {
                'nombre': 'Cerveza Club Colombia Dorada 330ml',
                'categoria': 'Cerveza',
                'marca': 'Club Colombia',
                'precio_compra': 2500,
                'precio_venta': 4200,
                'stock': random.randint(80, 250),
                'descripcion': 'Cerveza premium dorada'
            },
            {
                'nombre': 'Cerveza Club Colombia Negra 330ml',
                'categoria': 'Cerveza',
                'marca': 'Club Colombia',
                'precio_compra': 2600,
                'precio_venta': 4300,
                'stock': random.randint(70, 220),
                'descripcion': 'Cerveza premium negra'
            },
            {
                'nombre': 'Cerveza Corona Extra 355ml',
                'categoria': 'Cerveza',
                'marca': 'Corona',
                'precio_compra': 3500,
                'precio_venta': 6000,
                'stock': random.randint(60, 200),
                'descripcion': 'Cerveza mexicana importada'
            },
            {
                'nombre': 'Cerveza Águila Light 330ml',
                'categoria': 'Cerveza',
                'marca': 'Águila',
                'precio_compra': 2000,
                'precio_venta': 3500,
                'stock': random.randint(85, 260),
                'descripcion': 'Cerveza baja en calorías'
            },
            {
                'nombre': 'Cerveza Poker Light 330ml',
                'categoria': 'Cerveza',
                'marca': 'Poker',
                'precio_compra': 2100,
                'precio_venta': 3600,
                'stock': random.randint(75, 240),
                'descripcion': 'Cerveza ligera tradicional'
            },

            # Whiskys (5 productos)
            {
                'nombre': 'Buchanan\'s 12 Años',
                'categoria': 'Whisky',
                'marca': 'Buchanan\'s',
                'precio_compra': 95000,
                'precio_venta': 145000,
                'stock': random.randint(10, 35),
                'descripcion': 'Whisky escocés 12 años, 750ml'
            },
            {
                'nombre': 'Old Parr 12 Años',
                'categoria': 'Whisky',
                'marca': 'Old Parr',
                'precio_compra': 88000,
                'precio_venta': 135000,
                'stock': random.randint(12, 40),
                'descripcion': 'Whisky escocés premium, 750ml'
            },
            {
                'nombre': 'Johnnie Walker Red Label',
                'categoria': 'Whisky',
                'marca': 'Johnnie Walker',
                'precio_compra': 65000,
                'precio_venta': 105000,
                'stock': random.randint(15, 50),
                'descripcion': 'Whisky escocés etiqueta roja, 750ml'
            },
            {
                'nombre': 'Johnnie Walker Black Label',
                'categoria': 'Whisky',
                'marca': 'Johnnie Walker',
                'precio_compra': 92000,
                'precio_venta': 140000,
                'stock': random.randint(10, 40),
                'descripcion': 'Whisky escocés etiqueta negra, 750ml'
            },
            {
                'nombre': 'Buchanan\'s Special Reserve',
                'categoria': 'Whisky',
                'marca': 'Buchanan\'s',
                'precio_compra': 110000,
                'precio_venta': 170000,
                'stock': random.randint(8, 30),
                'descripcion': 'Whisky escocés reserva especial, 750ml'
            },

            # Vodkas (3 productos)
            {
                'nombre': 'Absolut Vodka Original',
                'categoria': 'Vodka',
                'marca': 'Absolut',
                'precio_compra': 52000,
                'precio_venta': 82000,
                'stock': random.randint(18, 60),
                'descripcion': 'Vodka sueco premium, 750ml'
            },
            {
                'nombre': 'Smirnoff Red',
                'categoria': 'Vodka',
                'marca': 'Smirnoff',
                'precio_compra': 42000,
                'precio_venta': 68000,
                'stock': random.randint(22, 70),
                'descripcion': 'Vodka clásico, 750ml'
            },
            {
                'nombre': 'Absolut Citron',
                'categoria': 'Vodka',
                'marca': 'Absolut',
                'precio_compra': 55000,
                'precio_venta': 85000,
                'stock': random.randint(15, 55),
                'descripcion': 'Vodka con sabor a limón, 750ml'
            },

            # Vinos (3 productos)
            {
                'nombre': 'Vino Gato Negro Cabernet Sauvignon',
                'categoria': 'Vino',
                'marca': 'Gato Negro',
                'precio_compra': 22000,
                'precio_venta': 38000,
                'stock': random.randint(25, 75),
                'descripcion': 'Vino tinto chileno, 750ml'
            },
            {
                'nombre': 'Vino Gato Negro Chardonnay',
                'categoria': 'Vino',
                'marca': 'Gato Negro',
                'precio_compra': 22000,
                'precio_venta': 38000,
                'stock': random.randint(20, 65),
                'descripcion': 'Vino blanco chileno, 750ml'
            },
            {
                'nombre': 'Vino Gato Negro Merlot',
                'categoria': 'Vino',
                'marca': 'Gato Negro',
                'precio_compra': 22000,
                'precio_venta': 38000,
                'stock': random.randint(18, 60),
                'descripcion': 'Vino tinto Merlot, 750ml'
            },

            # Tequilas (2 productos)
            {
                'nombre': 'Tequila Jose Cuervo Especial',
                'categoria': 'Tequila',
                'marca': 'Jose Cuervo',
                'precio_compra': 55000,
                'precio_venta': 88000,
                'stock': random.randint(15, 50),
                'descripcion': 'Tequila reposado mexicano, 750ml'
            },
            {
                'nombre': 'Tequila Jose Cuervo Silver',
                'categoria': 'Tequila',
                'marca': 'Jose Cuervo',
                'precio_compra': 52000,
                'precio_venta': 85000,
                'stock': random.randint(18, 55),
                'descripcion': 'Tequila blanco mexicano, 750ml'
            },
        ]

        for prod_data in productos:
            categoria = categorias.get(prod_data['categoria'])
            marca = marcas.get(prod_data['marca'])
            proveedor = random.choice(proveedores)

            producto = Producto.objects.create(
                nombre=prod_data['nombre'],
                precio_compra=Decimal(str(prod_data['precio_compra'])),
                precio_venta=Decimal(str(prod_data['precio_venta'])),
                stock=prod_data['stock'],
                descripcion=prod_data['descripcion'],
                id_categoria=categoria,
                id_marca=marca,
                id_proveedor=proveedor,
                activo=True
            )

            # Crear registro de stock inicial
            Stock.objects.create(
                id_producto=producto,
                cantidad=prod_data['stock']
            )

        self.stdout.write(self.style.SUCCESS(f'   ✓ {len(productos)} productos de licor creados'))

    def crear_mesas(self):
        """Crear mesas del restaurante/bar"""
        self.stdout.write('🪑 Creando mesas...')

        estados = ['disponible', 'ocupada', 'reservada']

        for i in range(1, 16):  # 15 mesas
            estado = random.choice(estados) if i > 3 else 'disponible'
            Mesa.objects.create(
                nombre=f'Mesa {i}',
                descripcion=f'Mesa para {random.choice([2, 4, 6, 8])} personas',
                estado=estado
            )

        self.stdout.write(self.style.SUCCESS('   ✓ 15 mesas creadas'))

    def crear_empleados(self):
        """Crear empleados vinculados a usuarios"""
        self.stdout.write('👔 Creando empleados...')

        # Obtener usuarios sin empleado
        usuarios = User.objects.filter(empleado__isnull=True)[:5]

        cargos = ['Mesero', 'Bartender', 'Cajero', 'Gerente', 'Cocinero']
        tipos_contrato = ['tiempo_completo', 'medio_tiempo', 'temporal']

        for i, user in enumerate(usuarios):
            Empleado.objects.create(
                user=user,
                nombre=f'{user.first_name} {user.last_name}',
                cargo=cargos[i % len(cargos)],
                salario=Decimal(str(random.randint(800000, 1200000))),
                fecha_contratacion=timezone.now().date() - timedelta(days=random.randint(30, 730)),
                estado='activo',
                tipo_contrato=random.choice(tipos_contrato),
                email=user.email,
                telefono=f'3{random.randint(100000000, 199999999)}',
                direccion=f'Calle {random.randint(1, 100)} #{random.randint(1, 50)}-{random.randint(1, 99)}'
            )

        self.stdout.write(self.style.SUCCESS(f'   ✓ {usuarios.count()} empleados creados'))

    def crear_expense_categories(self):
        """Crear categorías de gastos"""
        self.stdout.write('💰 Creando categorías de gastos...')

        categorias = [
            'Servicios Públicos',
            'Mantenimiento',
            'Publicidad',
            'Suministros de Oficina',
            'Transporte',
            'Gastos Operativos',
            'Gastos Extraordinarios'
        ]

        for nombre in categorias:
            ExpenseCategory.objects.get_or_create(name=nombre)

        self.stdout.write(self.style.SUCCESS(f'   ✓ {len(categorias)} categorías de gastos creadas'))

    def crear_gastos(self):
        """Crear gastos de ejemplo - proporcionales a los ingresos"""
        self.stdout.write('💸 Creando gastos...')

        categorias = list(ExpenseCategory.objects.all())
        usuarios = list(User.objects.filter(is_staff=True))

        if not categorias or not usuarios:
            self.stdout.write(self.style.WARNING('   ⚠ No hay categorías o usuarios para crear gastos'))
            return

        gastos_count = 0
        # Crear gastos más realistas - aproximadamente 30-40% de los ingresos totales
        # Ingresos totales: ~15M, gastos deberían ser 4-6M
        gastos_totales_objetivo = Decimal('5000000')  # 5M en gastos

        for i in range(40):  # 40 gastos distribuidos en últimos 60 días
            gasto_amount = Decimal(str(random.randint(50000, 200000)))  # Gastos más pequeños y realistas
            Expense.objects.create(
                date=timezone.now().date() - timedelta(days=random.randint(0, 60)),  # Mismo período que facturas
                amount=gasto_amount,
                category=random.choice(categorias),
                description=f'Gasto operativo - {random.choice(["Compra de insumos", "Pago de servicios", "Mantenimiento", "Reparación", "Suministros", "Servicios profesionales"])}',
                user=random.choice(usuarios)
            )
            gastos_count += 1

        self.stdout.write(self.style.SUCCESS(f'   ✓ {gastos_count} gastos creados (totales realistas: ~5M COP)'))

    def crear_pedidos_y_facturas(self):
        """Crear pedidos con items y facturas"""
        self.stdout.write('🧾 Creando pedidos y facturas...')

        mesas = list(Mesa.objects.all())
        productos = list(Producto.objects.filter(activo=True))
        usuarios = list(User.objects.all())

        if not productos:
            self.stdout.write(self.style.WARNING('   ⚠ No hay productos para crear pedidos'))
            return

        pedidos_count = 0
        facturas_count = 0

        for _ in range(30):  # 30 pedidos
            mesa = random.choice(mesas)

            # Generar fecha con más variabilidad - últimos 60 días para asegurar data en el mes actual
            # Usar números negativos para días hacia atrás
            dias_atras = random.randint(0, 60)
            fecha_pedido = timezone.now() - timedelta(days=dias_atras)

            pedido = Pedido.objects.create(
                mesa=mesa,
                fecha_creacion=fecha_pedido,
                estado='facturado'  # Todos los pedidos son facturados para garantizar ingresos
            )

            # Agregar usuarios al pedido
            pedido.usuarios.add(random.choice(usuarios))

            # Crear items del pedido (2-5 productos)
            num_items = random.randint(2, 5)
            total_pedido = Decimal('0')
            for _ in range(num_items):
                producto = random.choice(productos)
                cantidad = random.randint(1, 4)
                PedidoItem.objects.create(
                    pedido=pedido,
                    producto=producto,
                    cantidad=cantidad,
                    precio_unitario=producto.precio_venta
                )
                total_pedido += producto.precio_venta * cantidad

            pedidos_count += 1

            # Crear factura SIEMPRE para que haya ingresos
            # La fecha debe ser datetime con timezone, no solo date
            factura = Factura.objects.create(
                pedido=pedido,
                fecha=fecha_pedido,
                total=total_pedido or pedido.total()
            )
            facturas_count += 1

        self.stdout.write(self.style.SUCCESS(f'   ✓ {pedidos_count} pedidos y {facturas_count} facturas creadas'))

    def crear_nominas(self):
        """Crear pagos de nómina para empleados"""
        self.stdout.write('💵 Creando nóminas...')

        empleados = list(Empleado.objects.filter(estado='activo'))

        if not empleados:
            self.stdout.write(self.style.WARNING('   ⚠ No hay empleados activos para crear nóminas'))
            return

        pagos_count = 0
        bonificaciones_count = 0
        for empleado in empleados:
            # Crear 1-2 pagos por empleado (en lugar de 2-4)
            num_pagos = random.randint(1, 2)
            for i in range(num_pagos):
                fecha = timezone.now().date() - timedelta(days=30 * (i + 1))
                Pago.objects.create(
                    empleado=empleado,
                    fecha_pago=fecha,
                    monto=empleado.salario,
                    tipo='salario',
                    descripcion=f'Pago de nómina {fecha.strftime("%B %Y")}'
                )
                pagos_count += 1

                # Agregar bonificación ocasional
                if random.random() > 0.7:  # 30% de probabilidad
                    Bonificacion.objects.create(
                        empleado=empleado,
                        nombre=random.choice([
                            'Bonificación por desempeño',
                            'Prima de servicios',
                            'Bonificación navideña',
                            'Incentivo de ventas'
                        ]),
                        monto=Decimal(str(random.randint(100000, 300000))),
                        recurrente=False,
                        fecha_inicio=fecha,
                        activa=True
                    )
                    bonificaciones_count += 1

        self.stdout.write(self.style.SUCCESS(f'   ✓ {pagos_count} pagos y {bonificaciones_count} bonificaciones creadas'))

    def crear_reportes(self):
        """Crear reportes de ejemplo"""
        self.stdout.write('📊 Creando reportes...')

        usuarios = list(User.objects.filter(is_staff=True))

        if not usuarios:
            self.stdout.write(self.style.WARNING('   ⚠ No hay usuarios para crear reportes'))
            return

        tipos_reportes = ['ventas', 'inventario', 'gastos', 'nominas', 'productos', 'mesas']
        periodos = ['diario', 'semanal', 'mensual']
        formatos = ['pdf', 'excel', 'csv']

        reportes_count = 0
        for _ in range(20):  # 20 reportes
            fecha_inicio = timezone.now().date() - timedelta(days=random.randint(30, 180))
            fecha_fin = fecha_inicio + timedelta(days=random.randint(7, 30))

            Reporte.objects.create(
                nombre=f'Reporte de {random.choice(tipos_reportes)} - {fecha_inicio.strftime("%B %Y")}',
                tipo=random.choice(tipos_reportes),
                periodo=random.choice(periodos),
                formato=random.choice(formatos),
                descripcion=f'Reporte generado automáticamente para análisis',
                creado_por=random.choice(usuarios),
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                generado=random.choice([True, False])
            )
            reportes_count += 1

        self.stdout.write(self.style.SUCCESS(f'   ✓ {reportes_count} reportes creados'))
