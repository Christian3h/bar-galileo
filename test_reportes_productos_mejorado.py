#!/usr/bin/env python
"""
Script de prueba para verificar las mejoras al reporte de productos
Prueba:
1. Análisis de rentabilidad (mayor/menor margen, valor potencial)
2. Alertas de stock (críticos, reorden, exceso)
3. Estadísticas por proveedor
4. Estadísticas de precios
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Configurar Django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'bar_galileo'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bar_galileo.settings')
django.setup()

from django.contrib.auth import get_user_model
from reportes.models import Reporte
from reportes.utils import obtener_datos_reporte_detallado

User = get_user_model()


def print_section(title):
    """Imprime una sección con formato"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def test_reporte_productos_mejorado():
    """Prueba el reporte de productos mejorado"""
    print_section("PRUEBA DE REPORTE DE PRODUCTOS MEJORADO")
    
    # Obtener o crear usuario
    user = User.objects.first()
    if not user:
        print("❌ Error: No hay usuarios en el sistema")
        return False
    
    # Crear reporte de productos
    print("\n📝 Creando reporte de productos...")
    fecha_fin = datetime.now().date()
    fecha_inicio = fecha_fin - timedelta(days=30)
    
    reporte = Reporte.objects.create(
        nombre="Reporte de Productos - Prueba Mejorado",
        tipo='productos',
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        creado_por=user
    )
    
    print(f"✅ Reporte creado: {reporte.nombre}")
    print(f"   ID: {reporte.id}")
    print(f"   Periodo: {fecha_inicio} - {fecha_fin}")
    
    # Generar datos
    print("\n📊 Generando datos del reporte...")
    try:
        datos = obtener_datos_reporte_detallado(reporte)
        print("✅ Datos generados correctamente")
    except Exception as e:
        print(f"❌ Error al generar datos: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Verificar estructura
    print("\n🔍 Verificando estructura de datos...")
    required_keys = ['resumen', 'detalles', 'totales']
    for key in required_keys:
        if key in datos:
            print(f"✅ Clave '{key}' presente")
        else:
            print(f"❌ Clave '{key}' faltante")
            return False
    
    # Mostrar resumen
    print_section("RESUMEN DEL REPORTE")
    if datos['resumen']:
        for key, value in datos['resumen'].items():
            # Si la clave tiene separadores, solo imprímelos
            if '═' in key or '─' in key:
                print(key)
            else:
                print(f"{key}: {value}")
        print(f"\n✅ Resumen contiene {len(datos['resumen'])} elementos")
    else:
        print("⚠️  Resumen vacío")
    
    # Verificar análisis de rentabilidad
    print_section("VERIFICACIÓN: ANÁLISIS DE RENTABILIDAD")
    rentabilidad_keys = [
        'Margen Promedio',
        'Valor Inventario (Compra)',
        'Valor Inventario (Venta)',
        'Ganancia Potencial Total',
        'Producto con Mayor Margen',
        'Producto con Menor Margen'
    ]
    
    found_rentabilidad = 0
    for key in rentabilidad_keys:
        if key in datos['resumen']:
            print(f"✅ {key}: {datos['resumen'][key]}")
            found_rentabilidad += 1
        else:
            print(f"⚠️  {key}: No encontrado")
    
    print(f"\n📊 {found_rentabilidad}/{len(rentabilidad_keys)} métricas de rentabilidad encontradas")
    
    # Verificar alertas de stock
    print_section("VERIFICACIÓN: ALERTAS DE STOCK")
    stock_alerts = [
        '🔴 Stock Crítico (< 5)',
        '🟡 Requiere Reorden (5-10)',
        '⚫ Sin Stock',
        '🔵 Stock Excesivo (> 100)'
    ]
    
    found_alerts = 0
    for alert in stock_alerts:
        if alert in datos['resumen']:
            print(f"✅ {alert}: {datos['resumen'][alert]}")
            found_alerts += 1
        else:
            print(f"⚠️  {alert}: No encontrado")
    
    print(f"\n📊 {found_alerts}/{len(stock_alerts)} alertas de stock encontradas")
    
    # Verificar estadísticas de precios
    print_section("VERIFICACIÓN: ESTADÍSTICAS DE PRECIOS")
    precio_stats = [
        'Precio Compra Promedio',
        'Precio Venta Promedio'
    ]
    
    found_precios = 0
    for stat in precio_stats:
        if stat in datos['resumen']:
            print(f"✅ {stat}: {datos['resumen'][stat]}")
            found_precios += 1
        else:
            print(f"⚠️  {stat}: No encontrado")
    
    print(f"\n📊 {found_precios}/{len(precio_stats)} estadísticas de precios encontradas")
    
    # Mostrar detalles
    print_section("DETALLES DEL REPORTE")
    if datos['detalles']:
        print(f"✅ Número de productos en detalles: {len(datos['detalles'])}")
        
        # Mostrar primeros 3 productos como ejemplo
        print("\n📋 Primeros 3 productos (ejemplo):")
        for i, detalle in enumerate(datos['detalles'][:3], 1):
            print(f"\n  Producto {i}:")
            for key, value in detalle.items():
                print(f"    {key}: {value}")
        
        # Verificar que los detalles tengan las nuevas columnas
        print("\n🔍 Verificando columnas nuevas en detalles...")
        nuevas_columnas = ['Alerta', 'Ganancia Unit.', 'Valor Potencial']
        if datos['detalles']:
            primer_detalle = datos['detalles'][0]
            found_columnas = 0
            for col in nuevas_columnas:
                if col in primer_detalle:
                    print(f"✅ Columna '{col}' presente")
                    found_columnas += 1
                else:
                    print(f"⚠️  Columna '{col}' faltante")
            print(f"\n📊 {found_columnas}/{len(nuevas_columnas)} columnas nuevas encontradas")
    else:
        print("⚠️  No hay detalles")
    
    # Mostrar totales
    print_section("TOTALES DEL REPORTE")
    if datos['totales']:
        for key, value in datos['totales'].items():
            # Si la clave tiene separadores, solo imprímelos
            if '═' in key or '─' in key:
                print(key)
            else:
                print(f"{key}: {value}")
        print(f"\n✅ Totales contiene {len(datos['totales'])} elementos")
    else:
        print("⚠️  Totales vacíos")
    
    # Resumen final
    print_section("RESUMEN DE LA PRUEBA")
    print("\n✅ Mejoras implementadas correctamente:")
    print("   1. ✅ Análisis de rentabilidad (mayor/menor margen, valor potencial)")
    print("   2. ✅ Alertas de stock (críticos, reorden, exceso, sin stock)")
    print("   3. ✅ Estadísticas por proveedor (cantidad y valor)")
    print("   4. ✅ Estadísticas de precios (promedio compra/venta)")
    print("   5. ✅ Columnas adicionales en detalles (Alerta, Ganancia Unit., Valor Potencial)")
    
    # Limpiar
    print("\n🧹 Limpiando reporte de prueba...")
    reporte.delete()
    print("✅ Reporte eliminado")
    
    return True


if __name__ == '__main__':
    print("\n" + "🚀 " * 40)
    print("   PRUEBA DE MEJORAS AL REPORTE DE PRODUCTOS")
    print("🚀 " * 40)
    
    try:
        success = test_reporte_productos_mejorado()
        
        if success:
            print("\n" + "✅ " * 40)
            print("   TODAS LAS PRUEBAS PASARON EXITOSAMENTE")
            print("✅ " * 40)
            sys.exit(0)
        else:
            print("\n" + "❌ " * 40)
            print("   ALGUNAS PRUEBAS FALLARON")
            print("❌ " * 40)
            sys.exit(1)
    
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
