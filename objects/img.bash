#!/bin/bash

# Carpeta raíz donde están los objetos
BASE_DIR="objects"

# Recorrer todas las subcarpetas que contienen PDFs
find "$BASE_DIR" -type f -name "*.pdf" | while read pdf_file; do
    # Obtener la carpeta del PDF
    pdf_dir=$(dirname "$pdf_file")
    
    # Nombre base del PDF sin extensión
    pdf_base=$(basename "$pdf_file" .pdf)
    
    # Carpeta de destino para las imágenes
    image_dir="$pdf_dir/images"
    mkdir -p "$image_dir"
    
    # Prefijo para los nombres de las páginas
    image_prefix="$image_dir/${pdf_base}_page"
    
    # Ejecutar pdftoppm
    pdftoppm -jpeg "$pdf_file" "$image_prefix"
    
    echo "Procesado: $pdf_file"
done