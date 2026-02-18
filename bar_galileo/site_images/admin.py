from django.contrib import admin
from .models import SiteImageSection, SiteImage, CarouselImage, SiteContent


@admin.register(SiteContent)
class SiteContentAdmin(admin.ModelAdmin):
    list_display = ('section', 'updated_at')
    readonly_fields = ('updated_at',)


@admin.register(SiteImageSection)
class SiteImageSectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'section_type', 'created_at')
    list_filter = ('section_type',)
    search_fields = ('name', 'description')


@admin.register(SiteImage)
class SiteImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'section', 'is_active', 'order', 'get_file_size_display', 'created_at')
    list_filter = ('section', 'is_active')
    search_fields = ('title', 'alt_text')
    list_editable = ('is_active', 'order')
    readonly_fields = ('width', 'height', 'file_size', 'created_at', 'updated_at')


@admin.register(CarouselImage)
class CarouselImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'order', 'get_file_size_display', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('title', 'alt_text', 'caption')
    list_editable = ('is_active', 'order')
    readonly_fields = ('width', 'height', 'file_size', 'created_at', 'updated_at')
    fieldsets = (
        ('Información Básica', {
            'fields': ('title', 'image', 'alt_text')
        }),
        ('Contenido Adicional', {
            'fields': ('caption', 'link_url')
        }),
        ('Configuración', {
            'fields': ('order', 'is_active')
        }),
        ('Información del Archivo', {
            'fields': ('width', 'height', 'file_size', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
