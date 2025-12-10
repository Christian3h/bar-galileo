#!/usr/bin/env python
"""
Script de prueba para el módulo de reportes
Este script genera un reporte de prueba y verifica que funcione correctamente
"""

import os
import sys
import django
from datetime import date, timedelta

# Configurar Django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'bar_galileo'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bar_galileo.settings')
django.setup()

from django.contrib.auth.models import User
from reportes.models import Reporte
from reportes.utils import obtener_datos_reporte_detallado


def test_reportes():
    """Prueba la generación de reportes"""
    
    print("=" * 80)
    print("PRUEBA DEL MÓDULO DE REPORTES")
    print("=" * 80)
    print()
    
    # Obtener o crear usuario de prueba
    try:
        user = User.objects.first()
        if not user:
            user = User.objects.create_user(
                username='admin',
                email='admin@bar-galileo.com',
                password='admin123'
            )
            print(f"✓ Usuario de prueba creado: {user.username}")
        else:
            print(f"✓ Usuario encontrado: {user.username}")
    except Exception as e:
        print(f"✗ Error al obtener usuario: {e}")
        return
    
    print()
    
    # Tipos de reportes a probar
    tipos_reporte = [
        ('ventas', 'Reporte de Ventas de Prueba'),
        ('gastos', 'Reporte de Gastos de Prueba'),
        ('nominas', 'Reporte de Nóminas de Prueba'),
        ('inventario', 'Reporte de Inventario de Prueba'),
        ('productos', 'Reporte de Productos de Prueba'),
        ('mesas', 'Reporte de Mesas y Pedidos de Prueba'),
        ('general', 'Reporte General de Prueba'),
    ]
    
    fecha_inicio = date.today() - timedelta(days=30)
    fecha_fin = date.today()
    
    resultados = []
    
    for tipo, nombre in tipos_reporte:
        print(f"Probando reporte: {nombre}")
        print("-" * 80)
        
        try:
            # Crear reporte
            reporte = Reporte.objects.create(
                nombre=nombre,
                tipo=tipo,
                periodo='mensual',
                formato='pdf',
                descripcion=f'Reporte de prueba automático para {tipo}',
                creado_por=user,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin
            )
            print(f"  ✓ Reporte creado: ID {reporte.id}")
            
            # Generar datos
            datos = obtener_datos_reporte_detallado(reporte)
            print(f"  ✓ Datos generados correctamente")
            
            # Verificar estructura de datos
            if 'resumen' in datos:
                print(f"    - Resumen: {len(datos['resumen'])} items")
                for key, value in list(datos['resumen'].items())[:3]:
                    print(f"      • {key}: {value}")
            
            if 'detalles' in datos:
                print(f"    - Detalles: {len(datos['detalles'])} registros")
                if datos['detalles']:
                    print(f"      Columnas: {', '.join(datos['detalles'][0].keys())}")
            
            if 'totales' in datos:
                print(f"    - Totales: {len(datos['totales'])} items")
                for key, value in datos['totales'].items():
                    print(f"      • {key}: {value}")
            
            # Guardar datos en el reporte
            reporte.set_datos(datos)
            reporte.generado = True
            reporte.save()
            print(f"  ✓ Datos guardados en el reporte")
            
            resultados.append((tipo, 'OK', None))
            
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
            resultados.append((tipo, 'ERROR', str(e)))
        
        print()
    
    # Resumen final
    print("=" * 80)
    print("RESUMEN DE PRUEBAS")
    print("=" * 80)
    print()
    
    exitosos = sum(1 for _, status, _ in resultados if status == 'OK')
    fallidos = sum(1 for _, status, _ in resultados if status == 'ERROR')
    
    print(f"Pruebas exitosas: {exitosos}/{len(resultados)}")
    print(f"Pruebas fallidas: {fallidos}/{len(resultados)}")
    print()
    
    if fallidos > 0:
        print("Reportes con errores:")
        for tipo, status, error in resultados:
            if status == 'ERROR':
                print(f"  - {tipo}: {error}")
    
    print()
    print("=" * 80)
    
    # Mostrar reportes creados
    print("Reportes creados en la base de datos:")
    reportes = Reporte.objects.filter(nombre__contains='Prueba').order_by('-fecha_creacion')[:10]
    for r in reportes:
        status = "✓ Generado" if r.generado else "✗ Sin generar"
        print(f"  {status} - {r.nombre} (ID: {r.id}, Tipo: {r.tipo})")
    
    print()
    print("Para ver o exportar los reportes, accede a:")
    print("  http://localhost:8000/reportes/")
    print()


if __name__ == '__main__':
    try:
        test_reportes()
    except KeyboardInterrupt:
        print("\n\nPrueba interrumpida por el usuario")
    except Exception as e:
        print(f"\n\n✗ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
