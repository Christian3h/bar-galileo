"""
Script simple para convertir el manual de Markdown a PDF
Este script funciona en Windows sin dependencias complicadas
"""
import os
import sys
from pathlib import Path

# Agregar el path del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bar_galileo.settings')

import django
django.setup()

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER


def convert_markdown_to_pdf_simple(md_path: Path, pdf_path: Path):
    """Convierte Markdown a PDF usando ReportLab (sin dependencias de sistema)"""
    
    # Leer el contenido markdown
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Crear el PDF
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=letter,
        rightMargin=inch*0.75,
        leftMargin=inch*0.75,
        topMargin=inch,
        bottomMargin=inch
    )
    
    # Estilos
    styles = getSampleStyleSheet()
    story = []
    
    # Procesar el markdown línea por línea
    lines = content.split('\n')
    
    for line in lines:
        line = line.strip()
        
        if not line:
            story.append(Spacer(1, 0.2*inch))
            continue
        
        # Títulos H1
        if line.startswith('# '):
            text = line[2:].strip()
            style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor='#2c3e50',
                spaceAfter=12
            )
            story.append(Paragraph(text, style))
            story.append(Spacer(1, 0.3*inch))
        
        # Títulos H2
        elif line.startswith('## '):
            text = line[3:].strip()
            style = ParagraphStyle(
                'CustomHeading2',
                parent=styles['Heading2'],
                fontSize=18,
                textColor='#34495e',
                spaceAfter=10
            )
            story.append(Paragraph(text, style))
            story.append(Spacer(1, 0.2*inch))
        
        # Títulos H3
        elif line.startswith('### '):
            text = line[4:].strip()
            style = ParagraphStyle(
                'CustomHeading3',
                parent=styles['Heading3'],
                fontSize=14,
                textColor='#7f8c8d',
                spaceAfter=8
            )
            story.append(Paragraph(text, style))
        
        # Listas
        elif line.startswith('- ') or line.startswith('* ') or line.startswith('+ '):
            text = '• ' + line[2:].strip()
            story.append(Paragraph(text, styles['Normal']))
        
        # Texto normal
        else:
            # Escapar caracteres especiales de HTML
            text = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            # Mantener negritas y cursivas básicas
            text = text.replace('**', '<b>').replace('**', '</b>')
            text = text.replace('*', '<i>').replace('*', '</i>')
            
            try:
                story.append(Paragraph(text, styles['Normal']))
            except:
                # Si hay error, agregar texto plano
                story.append(Paragraph(line[:200], styles['Normal']))
    
    # Construir PDF
    doc.build(story)
    print(f"✅ PDF creado exitosamente: {pdf_path}")


if __name__ == '__main__':
    # Rutas
    md_path = BASE_DIR / 'docs' / 'manual_usuario.md'
    pdf_path = BASE_DIR / 'bar_galileo' / 'media' / 'rag_documents' / 'manual_usuario.pdf'
    
    # Crear directorio si no existe
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    
    print("📄 Convirtiendo Manual de Usuario a PDF...")
    print(f"   Origen: {md_path}")
    print(f"   Destino: {pdf_path}")
    
    try:
        convert_markdown_to_pdf_simple(md_path, pdf_path)
        print("\n🎉 ¡Conversión completada!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
