from django.http import HttpResponse
from django.template.loader import get_template
from django.conf import settings
import csv
import io
import os

try:
    import openpyxl
    from openpyxl.styles import Font, Alignment, PatternFill
    from openpyxl.utils import get_column_letter
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


def generar_csv_reporte(reporte, datos):
    """Generar reporte en formato CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="reporte_{reporte.nombre}.csv"'

    writer = csv.writer(response)
    
    # Encabezados del reporte
    writer.writerow(['Reporte:', reporte.nombre])
    writer.writerow(['Tipo:', reporte.get_tipo_display()])
    writer.writerow(['Periodo:', f"{reporte.fecha_inicio} - {reporte.fecha_fin}"])
    writer.writerow(['Creado por:', str(reporte.creado_por)])
    writer.writerow(['Fecha de creación:', reporte.fecha_creacion.strftime('%d/%m/%Y %H:%M')])
    writer.writerow([])  # Línea vacía
    
    # Datos
    writer.writerow(['Concepto', 'Valor'])
    for key, value in datos.items():
        writer.writerow([key, value])

    return response


def generar_excel_reporte(reporte, datos):
    """Generar reporte en formato Excel (XLSX)"""
    if not OPENPYXL_AVAILABLE:
        raise ImportError("openpyxl no está disponible para exportar a Excel")
    
    # Crear workbook y worksheet
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Reporte"

    # Estilos
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
    header_alignment = Alignment(horizontal="center", vertical="center")
    
    title_font = Font(bold=True, size=14)
    
    # Información del reporte
    ws['A1'] = 'REPORTE - BAR GALILEO'
    ws['A1'].font = title_font
    ws.merge_cells('A1:B1')
    
    ws['A3'] = 'Nombre:'
    ws['B3'] = reporte.nombre
    ws['A4'] = 'Tipo:'
    ws['B4'] = reporte.get_tipo_display()
    ws['A5'] = 'Periodo:'
    ws['B5'] = f"{reporte.fecha_inicio} - {reporte.fecha_fin}"
    ws['A6'] = 'Creado por:'
    ws['B6'] = str(reporte.creado_por)
    ws['A7'] = 'Fecha de creación:'
    ws['B7'] = reporte.fecha_creacion.strftime('%d/%m/%Y %H:%M')
    
    # Encabezados de datos
    row = 9
    ws[f'A{row}'] = 'Concepto'
    ws[f'B{row}'] = 'Valor'
    
    # Aplicar estilo a encabezados
    for col in ['A', 'B']:
        cell = ws[f'{col}{row}']
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_alignment

    # Datos
    row += 1
    for key, value in datos.items():
        ws[f'A{row}'] = key
        ws[f'B{row}'] = str(value)
        row += 1

    # Ajustar ancho de columnas
    ws.column_dimensions['A'].width = 25
    ws.column_dimensions['B'].width = 20

    # Crear la respuesta HTTP
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="reporte_{reporte.nombre}.xlsx"'

    # Guardar workbook en la respuesta
    wb.save(response)
    return response


def generar_pdf_reporte(reporte, datos):
    """Generar reporte en formato PDF"""
    if not REPORTLAB_AVAILABLE:
        raise ImportError("reportlab no está disponible para exportar a PDF")
    
    # Crear la respuesta HTTP
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="reporte_{reporte.nombre}.pdf"'

    # Crear PDF
    doc = SimpleDocTemplate(response, pagesize=A4)
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        alignment=1,  # Centrado
        spaceAfter=30,
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        spaceAfter=15,
    )

    # Título
    title = Paragraph("Reporte - Bar Galileo", title_style)
    elements.append(title)
    elements.append(Spacer(1, 12))
    
    # Información del reporte
    info_data = [
        ['Nombre:', reporte.nombre],
        ['Tipo:', reporte.get_tipo_display()],
        ['Periodo:', f"{reporte.fecha_inicio.strftime('%d/%m/%Y')} - {reporte.fecha_fin.strftime('%d/%m/%Y')}"],
        ['Creado por:', str(reporte.creado_por)],
        ['Fecha de creación:', reporte.fecha_creacion.strftime('%d/%m/%Y %H:%M')]
    ]
    
    info_table = Table(info_data)
    info_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 20),
    ]))
    
    elements.append(info_table)
    elements.append(Spacer(1, 20))

    # Datos del reporte
    subtitle = Paragraph("Datos del Reporte", subtitle_style)
    elements.append(subtitle)
    
    # Preparar datos para la tabla
    data = [['Concepto', 'Valor']]
    
    for key, value in datos.items():
        data.append([key, str(value)])

    # Crear tabla de datos
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    elements.append(table)
    
    # Construir PDF
    doc.build(elements)
    return response
