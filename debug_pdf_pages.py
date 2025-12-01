#!/usr/bin/env python3
"""
Script de diagnostic pour comprendre pourquoi PyMuPDF compte
plus de pages que Adobe Reader.
"""

import sys

def diagnose_pdf(pdf_path: str):
    """Analyse un PDF et affiche des informations de diagnostic."""

    print(f"\n{'='*60}")
    print(f"DIAGNOSTIC PDF: {pdf_path}")
    print(f"{'='*60}\n")

    # 1. PyMuPDF (fitz)
    try:
        import pymupdf as fitz
    except ImportError:
        import fitz

    doc = fitz.open(pdf_path)

    print(f"📊 PyMuPDF (fitz):")
    print(f"   • Nombre de pages: {len(doc)}")
    print(f"   • page_count: {doc.page_count}")
    print(f"   • is_pdf: {doc.is_pdf}")
    print(f"   • is_encrypted: {doc.is_encrypted}")
    print(f"   • metadata: {doc.metadata}")

    # Vérifier les embedded files (pièces jointes)
    embedded_count = doc.embfile_count()
    print(f"   • Fichiers embeddés: {embedded_count}")

    if embedded_count > 0:
        print(f"   • Liste des fichiers embeddés:")
        for i in range(embedded_count):
            info = doc.embfile_info(i)
            print(f"     - {info.get('name', 'unknown')}: {info.get('length', 0)} bytes")

    # Vérifier si c'est un PDF Portfolio
    try:
        catalog = doc.pdf_catalog()
        print(f"   • PDF Catalog: {catalog}")
    except:
        pass

    # Analyser les premières et dernières pages
    print(f"\n📄 Analyse des pages:")

    # Pages avec contenu vs pages vides
    pages_with_text = 0
    pages_with_images = 0
    empty_pages = 0

    for i in range(min(len(doc), 100)):  # Limiter à 100 pour la vitesse
        page = doc[i]
        text = page.get_text()
        images = page.get_images()

        if text.strip():
            pages_with_text += 1
        if images:
            pages_with_images += 1
        if not text.strip() and not images:
            empty_pages += 1

    sample_size = min(len(doc), 100)
    print(f"   • (Sur les {sample_size} premières pages)")
    print(f"   • Pages avec texte: {pages_with_text}")
    print(f"   • Pages avec images: {pages_with_images}")
    print(f"   • Pages vides: {empty_pages}")

    # Taille des pages (détecter si format bizarre)
    print(f"\n📐 Dimensions des pages:")
    unique_sizes = set()
    for i in range(min(len(doc), 20)):
        page = doc[i]
        rect = page.rect
        size = (round(rect.width), round(rect.height))
        unique_sizes.add(size)

    for size in unique_sizes:
        print(f"   • {size[0]} x {size[1]} points")

    # 2. pdfplumber
    print(f"\n📊 pdfplumber:")
    try:
        import pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            print(f"   • Nombre de pages: {len(pdf.pages)}")
    except Exception as e:
        print(f"   • Erreur: {e}")

    # 3. PyPDF2
    print(f"\n📊 PyPDF2:")
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(pdf_path)
        print(f"   • Nombre de pages: {len(reader.pages)}")
    except ImportError:
        print(f"   • Non installé")
    except Exception as e:
        print(f"   • Erreur: {e}")

    doc.close()

    print(f"\n{'='*60}")
    print(f"CONCLUSION:")
    print(f"{'='*60}")

    if embedded_count > 0:
        print(f"⚠️  Le PDF contient {embedded_count} fichiers embeddés (pièces jointes)")
        print(f"   Ces fichiers pourraient expliquer le nombre de pages élevé.")

    if empty_pages > sample_size * 0.5:
        print(f"⚠️  Plus de 50% des pages sont vides - PDF potentiellement corrompu")

    print()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python debug_pdf_pages.py <chemin_du_pdf>")
        sys.exit(1)

    diagnose_pdf(sys.argv[1])
