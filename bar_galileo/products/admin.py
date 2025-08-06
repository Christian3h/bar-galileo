from django.contrib import admin
from .models import Producto, Categoria, Marca, Proveedor, ProductoImagen, Stock


class ProductoImagenInline(admin.TabularInline):
    model = ProductoImagen
    extra = 1


class StockInline(admin.TabularInline):
    model = Stock
    extra = 0
    readonly_fields = ('fecha_hora',)


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio_compra', 'precio_venta', 'stock', 'id_categoria', 'id_proveedor', 'id_marca')
    list_filter = ('id_categoria', 'id_proveedor', 'id_marca')
    search_fields = ('nombre', 'descripcion')
    inlines = [ProductoImagenInline, StockInline]
    
    def save_model(self, request, obj, form, change):
        # Guardar el producto primero
        super().save_model(request, obj, form, change)
        
        # Si el stock cambió, crear un registro en la tabla Stock
        if 'stock' in form.changed_data:
            Stock.objects.create(
                id_producto=obj,
                cantidad=obj.stock or 0
            )


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre_categoria', 'descripcion')
    search_fields = ('nombre_categoria',)


@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    list_display = ('marca', 'descripcion')
    search_fields = ('marca',)


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'contacto', 'telefono', 'direccion')
    search_fields = ('nombre', 'contacto')


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('id_producto', 'cantidad', 'fecha_hora')
    list_filter = ('fecha_hora',)
    readonly_fields = ('fecha_hora',)
    ordering = ('-fecha_hora',)
