from django.db import models, connection
from django.utils import timezone
from tables.models import Factura as FacturaOriginal
from decimal import InvalidOperation, Decimal
import logging

logger = logging.getLogger(__name__)

class FacturaSegura:
    """
    Clase wrapper para manejar facturas de forma segura
    """
    def __init__(self, id, numero, total, fecha, pedido_id, mesa_nombre=None):
        self.id = id
        self.numero = numero
        self._total_raw = total
        self.fecha = fecha
        self.pedido_id = pedido_id
        self.mesa_nombre = mesa_nombre
    
    @property
    def total(self):
        try:
            if self._total_raw is not None:
                return Decimal(str(self._total_raw))
            return Decimal('0')
        except (InvalidOperation, ValueError):
            return Decimal('0')
    
    @property
    def total_display(self):
        """
        Muestra el total en formato de precio colombiano
        """
        from django.contrib.humanize.templatetags.humanize import intcomma
        price_int = int(round(float(self.total)))
        formatted_price = intcomma(price_int).replace(',', '.')
        return f"${formatted_price}"

class FacturacionManager:
    """
    Manager personalizado para manejar operaciones de facturación
    """
    
    @staticmethod
    def obtener_facturas_con_filtros(busqueda=None, fecha_inicio=None, fecha_fin=None):
        """
        Obtiene facturas con filtros opcionales usando SQL directo
        """
        with connection.cursor() as cursor:
            # Consulta base con JOIN para obtener datos de mesa
            sql = """
                SELECT 
                    f.id, 
                    f.numero, 
                    f.total, 
                    f.fecha, 
                    f.pedido_id,
                    m.nombre as mesa_nombre
                FROM tables_factura f
                LEFT JOIN tables_pedido p ON f.pedido_id = p.id
                LEFT JOIN tables_mesa m ON p.mesa_id = m.id
                WHERE 1=1
            """
            params = []
            
            # Agregar filtros
            if busqueda:
                sql += " AND (f.numero LIKE %s OR m.nombre LIKE %s)"
                params.extend([f'%{busqueda}%', f'%{busqueda}%'])
            
            if fecha_inicio:
                sql += " AND DATE(f.fecha) >= %s"
                params.append(fecha_inicio.date())
            
            if fecha_fin:
                sql += " AND DATE(f.fecha) <= %s"
                params.append(fecha_fin.date())
            
            sql += " ORDER BY f.fecha DESC"
            
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            
            # Convertir a objetos FacturaSegura
            facturas = []
            for row in rows:
                facturas.append(FacturaSegura(
                    id=row[0],
                    numero=row[1],
                    total=row[2],
                    fecha=row[3],
                    pedido_id=row[4],
                    mesa_nombre=row[5]
                ))
            
            return facturas
    
    @staticmethod
    def obtener_estadisticas():
        """
        Obtiene estadísticas básicas de facturación usando SQL directo
        """
        try:
            with connection.cursor() as cursor:
                # Total de facturas
                cursor.execute("SELECT COUNT(*) FROM tables_factura")
                total_facturas = cursor.fetchone()[0]
                
                # Ingresos totales
                cursor.execute("SELECT SUM(CAST(total AS REAL)) FROM tables_factura WHERE total IS NOT NULL")
                total_ingresos_raw = cursor.fetchone()[0]
                total_ingresos = float(total_ingresos_raw) if total_ingresos_raw else 0
                
                # Facturas de hoy (simplificado)
                cursor.execute("SELECT COUNT(*) FROM tables_factura WHERE DATE(fecha) = DATE('now')")
                facturas_hoy = cursor.fetchone()[0]
                
                # Ingresos de hoy (simplificado)
                cursor.execute("SELECT SUM(CAST(total AS REAL)) FROM tables_factura WHERE DATE(fecha) = DATE('now') AND total IS NOT NULL")
                ingresos_hoy_raw = cursor.fetchone()[0]
                ingresos_hoy = float(ingresos_hoy_raw) if ingresos_hoy_raw else 0
                
                return {
                    'total_facturas': total_facturas,
                    'total_ingresos': total_ingresos,
                    'facturas_hoy': facturas_hoy,
                    'ingresos_hoy': ingresos_hoy,
                }
                
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {
                'total_facturas': 0,
                'total_ingresos': 0,
                'facturas_hoy': 0,
                'ingresos_hoy': 0,
            }
    
    @staticmethod
    def obtener_factura_por_id(factura_id):
        """
        Obtiene una factura específica por ID
        """
        try:
            return FacturaOriginal.objects.get(id=factura_id)
        except FacturaOriginal.DoesNotExist:
            return None
