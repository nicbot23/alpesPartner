#!/usr/bin/env python3

import PyPDF2
import sys

def extract_pdf_text(pdf_path, output_path):
    """Extraer texto de un PDF y guardarlo en un archivo de texto"""
    try:
        with open(pdf_path, 'rb') as pdf_file:
            # Crear objeto PDF reader
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            # Extraer texto de todas las páginas
            text = ""
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += f"\n--- PÁGINA {page_num + 1} ---\n"
                text += page.extract_text()
                text += "\n"
            
            # Guardar texto en archivo
            with open(output_path, 'w', encoding='utf-8') as text_file:
                text_file.write(text)
                
            print(f"✅ Texto extraído de {pdf_path} y guardado en {output_path}")
            print(f"📄 Total de páginas: {len(pdf_reader.pages)}")
            print(f"📝 Caracteres extraídos: {len(text)}")
            
    except Exception as e:
        print(f"❌ Error extrayendo texto de {pdf_path}: {e}")

if __name__ == "__main__":
    # Extraer ambos PDFs
    extract_pdf_text("Entrega-004y005-POCArquitecturaEnunciado.pdf", "enunciado.txt")
    extract_pdf_text("003-EntregaTemplate.pdf", "template.txt")
