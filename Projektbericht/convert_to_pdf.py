#!/usr/bin/env python3
"""
Konvertiert Word-Dokument (.docx) zu PDF
Benötigt: python-docx und python-pptx
"""

from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
import os
import subprocess
import sys

def convert_docx_to_pdf_via_libreoffice(docx_path, output_pdf_path):
    """
    Konvertiert DOCX zu PDF mit LibreOffice (wenn installiert)
    LibreOffice ist auf Windows meist verfügbar
    """
    try:
        # Versuche LibreOffice zu nutzen (am meisten verbreitet auf Windows)
        cmd = [
            'soffice',
            '--headless',
            '--convert-to', 'pdf',
            '--outdir', os.path.dirname(output_pdf_path),
            docx_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print(f'✅ PDF erstellt via LibreOffice: {output_pdf_path}')
            return True
        else:
            print(f'⚠️ LibreOffice Fehler: {result.stderr}')
            return False
            
    except FileNotFoundError:
        print('⚠️ LibreOffice nicht gefunden, versuche alternative Methode...')
        return False
    except Exception as e:
        print(f'⚠️ LibreOffice Fehler: {e}')
        return False

def convert_docx_to_pdf_via_docx2pdf(docx_path, output_pdf_path):
    """
    Konvertiert DOCX zu PDF mit docx2pdf Modul
    """
    try:
        from docx2pdf import convert
        convert(docx_path, output_pdf_path)
        print(f'✅ PDF erstellt via docx2pdf: {output_pdf_path}')
        return True
    except ImportError:
        print('⚠️ docx2pdf nicht installiert')
        return False
    except Exception as e:
        print(f'⚠️ docx2pdf Fehler: {e}')
        return False

def convert_docx_to_pdf_via_reportlab(docx_path, output_pdf_path):
    """
    Konvertiert DOCX zu PDF mit reportlab (Fallback)
    Behält grundlegende Formatierung
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
        from reportlab.lib.units import cm
        from reportlab.lib import colors
        
        doc = Document(docx_path)
        
        pdf_doc = SimpleDocTemplate(
            output_pdf_path,
            pagesize=A4,
            topMargin=2*cm,
            bottomMargin=2*cm,
            leftMargin=2*cm,
            rightMargin=2*cm
        )
        
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles für Formalia
        normal_style = ParagraphStyle(
            'Normal',
            parent=styles['Normal'],
            fontName='Arial',
            fontSize=11,
            leading=16.5,  # 1.5x Zeilenabstand
            alignment=4  # Justify
        )
        
        heading_style = ParagraphStyle(
            'Heading',
            parent=styles['Heading1'],
            fontName='Arial',
            fontSize=12,
            leading=18,
            spaceAfter=12,
            alignment=0
        )
        
        for para in doc.paragraphs:
            text = para.text.strip()
            if not text:
                story.append(Spacer(1, 0.3*cm))
                continue
            
            # Erkenne Überschriften
            is_heading = any(
                text.startswith(prefix) 
                for prefix in ['1.', '2.', '3.', '4.', 'INHALTS', 'LITERATUR', 'ANHANG', 'ABBKÜRZUNGS', 'TABELLEN']
            )
            
            if is_heading:
                story.append(Paragraph(f'<b>{text}</b>', heading_style))
            else:
                story.append(Paragraph(text, normal_style))
        
        pdf_doc.build(story)
        print(f'✅ PDF erstellt via reportlab: {output_pdf_path}')
        return True
        
    except ImportError:
        print('⚠️ reportlab nicht installiert')
        return False
    except Exception as e:
        print(f'⚠️ reportlab Fehler: {e}')
        return False

def main():
    docx_file = 'c:\\Users\\tizia\\Documents\\GitHub\\PythonOnlineShop\\Projektbericht\\Projektbericht_Webshop_FORMAL_KORREKT.docx'
    pdf_file = 'c:\\Users\\tizia\\Documents\\GitHub\\PythonOnlineShop\\Projektbericht\\Projektbericht_Webshop_FORMAL_KORREKT.pdf'
    
    print(f'🔄 Konvertiere DOCX zu PDF...')
    print(f'   Input:  {docx_file}')
    print(f'   Output: {pdf_file}')
    print()
    
    # Versuche Konvertierungsmethoden der Reihe nach
    success = False
    
    # Methode 1: LibreOffice (beste Qualität)
    print('📄 Versuche Methode 1: LibreOffice...')
    success = convert_docx_to_pdf_via_libreoffice(docx_file, pdf_file)
    
    if not success:
        # Methode 2: docx2pdf
        print('📄 Versuche Methode 2: docx2pdf...')
        success = convert_docx_to_pdf_via_docx2pdf(docx_file, pdf_file)
    
    if not success:
        # Methode 3: reportlab (Fallback)
        print('📄 Versuche Methode 3: reportlab (vereinfacht)...')
        success = convert_docx_to_pdf_via_reportlab(docx_file, pdf_file)
    
    if success:
        if os.path.exists(pdf_file):
            file_size = os.path.getsize(pdf_file) / 1024
            print(f'\n✅ ERFOLG! PDF erstellt ({file_size:.1f} KB)')
    else:
        print(f'\n❌ Alle Konvertierungsmethoden fehlgeschlagen')
        print(f'   Bitte installiere eine dieser Optionen:')
        print(f'   • LibreOffice (Windows: winget install libreoffice)')
        print(f'   • python-docx2pdf (pip install docx2pdf)')
        print(f'   • reportlab (pip install reportlab)')

if __name__ == '__main__':
    main()
