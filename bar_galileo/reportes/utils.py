"""
Utilidades para generar reportes en PDF y Excel

Nota: los paquetes de PDF/Excel se importan de forma diferida (lazy import)
para evitar que toda la app falle si no están instalados hasta el momento de exportar.
"""
from django.http import HttpResponse
from django.template.loader import render_to_string
from io import BytesIO
from datetime import datetime

# No importamos xlsxwriter/reportlab en módulo: los cargamos dentro de cada función


def generar_pdf_reporte(reporte, datos=None):
    """
    Genera un PDF del reporte
    """
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import (
            SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        )
        from reportlab.lib.enums import TA_CENTER
    except Exception as e:
        return HttpResponse(
            f"No se pudo generar el PDF: faltan dependencias (reportlab). Detalle: {e}",
            status=500
        )
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="reporte_{reporte.nombre.replace(" ", "_")}_{datetime.now().strftime("%Y%m%d")}.pdf"'
    
    # Crear el PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    # Contenedor para elementos
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#d4af37'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#d4af37'),
        spaceAfter=12,
    )
    
    normal_style = styles['Normal']
    
    # Título
    title = Paragraph(f"<b>{reporte.nombre}</b>", title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.2*inch))
    
    # Información del reporte
    info_data = [
        ['Tipo:', reporte.get_tipo_display()],
        ['Periodo:', reporte.get_periodo_display()],
        ['Fecha Inicio:', reporte.fecha_inicio.strftime('%d/%m/%Y')],
        ['Fecha Fin:', reporte.fecha_fin.strftime('%d/%m/%Y')],
        ['Creado por:', reporte.creado_por.get_full_name() or reporte.creado_por.username],
        ['Fecha de Creación:', reporte.fecha_creacion.strftime('%d/%m/%Y %H:%M')],
    ]
    
    info_table = Table(info_data, colWidths=[2*inch, 4*inch])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#3a3a3a')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#d4af37')),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.white),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    
    elements.append(info_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Descripción
    if reporte.descripcion:
        desc_heading = Paragraph("<b>Descripción:</b>", heading_style)
        elements.append(desc_heading)
        desc_text = Paragraph(reporte.descripcion, normal_style)
        elements.append(desc_text)
        elements.append(Spacer(1, 0.2*inch))
    
    # Datos adicionales (si existen)
    if datos:
        data_heading = Paragraph("<b>Datos del Reporte:</b>", heading_style)
        elements.append(data_heading)
        elements.append(Spacer(1, 0.1*inch))
        
        # Aquí puedes agregar lógica específica según el tipo de reporte
        # Por ahora, mostramos un resumen básico
        if isinstance(datos, dict):
            data_items = [[k, str(v)] for k, v in datos.items()]
            data_table = Table(data_items, colWidths=[3*inch, 3*inch])
            data_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d4af37')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            elements.append(data_table)
    
    # Generar PDF
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    
    return response


def generar_excel_reporte(reporte, datos=None):
    """
    Genera un Excel del reporte
    """
    try:
        import xlsxwriter
    except Exception as e:
        return HttpResponse(
            f"No se pudo generar el Excel: faltan dependencias (xlsxwriter). Detalle: {e}",
            status=500
        )
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="reporte_{reporte.nombre.replace(" ", "_")}_{datetime.now().strftime("%Y%m%d")}.xlsx"'
    
    # Crear el workbook
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet('Reporte')
    
    # Formatos
    title_format = workbook.add_format({
        'bold': True,
        'font_size': 18,
        'font_color': '#d4af37',
        'align': 'center',
        'valign': 'vcenter'
    })
    
    header_format = workbook.add_format({
        'bold': True,
        'font_size': 12,
        'bg_color': '#3a3a3a',
        'font_color': '#d4af37',
        'border': 1
    })
    
    cell_format = workbook.add_format({
        'font_size': 10,
        'border': 1,
        'align': 'left',
        'valign': 'vcenter'
    })
    
    date_format = workbook.add_format({
        'font_size': 10,
        'border': 1,
        'num_format': 'dd/mm/yyyy'
    })
    
    # Título
    worksheet.merge_range('A1:B1', reporte.nombre, title_format)
    worksheet.set_row(0, 30)
    
    # Información del reporte
    row = 2
    worksheet.write(row, 0, 'Tipo:', header_format)
    worksheet.write(row, 1, reporte.get_tipo_display(), cell_format)
    
    row += 1
    worksheet.write(row, 0, 'Periodo:', header_format)
    worksheet.write(row, 1, reporte.get_periodo_display(), cell_format)
    
    row += 1
    worksheet.write(row, 0, 'Fecha Inicio:', header_format)
    worksheet.write_datetime(row, 1, reporte.fecha_inicio, date_format)
    
    row += 1
    worksheet.write(row, 0, 'Fecha Fin:', header_format)
    worksheet.write_datetime(row, 1, reporte.fecha_fin, date_format)
    
    row += 1
    worksheet.write(row, 0, 'Creado por:', header_format)
    worksheet.write(row, 1, reporte.creado_por.get_full_name() or reporte.creado_por.username, cell_format)
    
    row += 1
    worksheet.write(row, 0, 'Fecha de Creación:', header_format)
    worksheet.write(row, 1, reporte.fecha_creacion.strftime('%d/%m/%Y %H:%M'), cell_format)
    
    # Descripción
    if reporte.descripcion:
        row += 2
        worksheet.write(row, 0, 'Descripción:', header_format)
        worksheet.merge_range(row, 1, row, 5, reporte.descripcion, cell_format)
    
    # Ajustar columnas
    worksheet.set_column('A:A', 20)
    worksheet.set_column('B:F', 25)
    
    # Datos adicionales (si existen)
    if datos and isinstance(datos, dict):
        row += 2
        worksheet.write(row, 0, 'DATOS DEL REPORTE', header_format)
        row += 1
        
        for key, value in datos.items():
            worksheet.write(row, 0, key, header_format)
            worksheet.write(row, 1, str(value), cell_format)
            row += 1
    
    workbook.close()
    output.seek(0)
    response.write(output.read())
    
    return response


def generar_csv_reporte(reporte, datos=None):
    """
    Genera un CSV del reporte
    """
    import csv
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="reporte_{reporte.nombre.replace(" ", "_")}_{datetime.now().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    
    # Encabezados
    writer.writerow(['REPORTE:', reporte.nombre])
    writer.writerow([])
    writer.writerow(['Tipo', reporte.get_tipo_display()])
    writer.writerow(['Periodo', reporte.get_periodo_display()])
    writer.writerow(['Fecha Inicio', reporte.fecha_inicio.strftime('%d/%m/%Y')])
    writer.writerow(['Fecha Fin', reporte.fecha_fin.strftime('%d/%m/%Y')])
    writer.writerow(['Creado por', reporte.creado_por.get_full_name() or reporte.creado_por.username])
    writer.writerow(['Fecha de Creación', reporte.fecha_creacion.strftime('%d/%m/%Y %H:%M')])
    
    if reporte.descripcion:
        writer.writerow([])
        writer.writerow(['Descripción', reporte.descripcion])
    
    if datos and isinstance(datos, dict):
        writer.writerow([])
        writer.writerow(['DATOS DEL REPORTE'])
        for key, value in datos.items():
            writer.writerow([key, value])
    
    return response
