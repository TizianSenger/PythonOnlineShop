#!/usr/bin/env python3
"""
Konvertiert DOCX zu PDF mit Python-native Methode
Nutzt Microsoft Word COM Objekt auf Windows
"""

import os
import sys
import time

def convert_word_to_pdf_via_com():
    """
    Nutzt Microsoft Word COM Objekt zur Konvertierung
    (Windows only, benötigt Microsoft Office)
    """
    try:
        import win32com.client
        
        # Pfade
        docx_file = r'c:\Users\tizia\Documents\GitHub\PythonOnlineShop\Projektbericht\Projektbericht_Webshop_FORMAL_KORREKT.docx'
        pdf_file = r'c:\Users\tizia\Documents\GitHub\PythonOnlineShop\Projektbericht\Projektbericht_Webshop_FORMAL_KORREKT.pdf'
        
        print('📄 Starte Microsoft Word COM Objekt...')
        
        # Word Objekt erzeugen
        word = win32com.client.Dispatch('Word.Application')
        word.Visible = False
        
        # Dokument öffnen
        doc = word.Documents.Open(os.path.abspath(docx_file))
        
        print('📄 Konvertiere zu PDF...')
        
        # Als PDF speichern
        doc.SaveAs(
            os.path.abspath(pdf_file),
            FileFormat=17  # 17 = wdFormatPDF
        )
        
        doc.Close()
        word.Quit()
        
        print(f'✅ PDF erfolgreich erstellt!')
        print(f'   Datei: {pdf_file}')
        
        if os.path.exists(pdf_file):
            size = os.path.getsize(pdf_file) / 1024
            print(f'   Größe: {size:.1f} KB')
        
        return True
        
    except ImportError:
        print('⚠️ pywin32 nicht vollständig installiert')
        return False
    except Exception as e:
        print(f'⚠️ Fehler: {e}')
        return False

if __name__ == '__main__':
    success = convert_word_to_pdf_via_com()
    sys.exit(0 if success else 1)
