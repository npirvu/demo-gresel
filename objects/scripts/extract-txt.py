#!/usr/bin/env python3
"""
Extract text from newspaper JSON files and create corresponding TXT files.

This script processes all JSON files under objects/newspapers/ following the
structure: pages → textRegions → textLines, processes the text to restore
proper formatting, and creates text files in the same directory structure.
"""

import json
import os
import re
from pathlib import Path


def restore_text_lines(text):
    """
    Restore text lines by joining split paragraphs and cleaning up formatting.
    
    Args:
        text: Input text with potentially split lines
        
    Returns:
        Restored and cleaned text
    """
    # Split by double newlines to get paragraphs
    paragraphs = text.split('\n\n')
    
    restored_paragraphs = []
    
    for paragraph in paragraphs:
        # Strip whitespace
        paragraph = paragraph.strip()
        
        if not paragraph:
            continue
        
        # Join all lines within this paragraph into a single line
        lines = paragraph.split('\n')
        joined = ' '.join(line.strip() for line in lines if line.strip())
        
        restored_paragraphs.append(joined)
    
    # Join paragraphs back with single newlines
    text = '\n'.join(restored_paragraphs)
        
    # Remove soft hyphens
    text = re.sub(r'¬\s*', '', text)
    text = re.sub(r'-\s*', '', text)
    
    # Fix double spaces
    text = re.sub(r'  +', ' ', text)
    
    return text


def extract_text_from_json(json_path):
    """
    Extract text content from a newspaper JSON file.
    
    The JSON structure is:
    - pages (array)
      - textRegions (array)
        - text (string) - region-level text
        - textLines (array)
          - text (string) - line-level text
    
    Args:
        json_path: Path to the JSON file
        
    Returns:
        Extracted text as a string, or None if extraction fails
    """
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, dict) or 'pages' not in data:
            print(f"  Warning: Unexpected JSON structure in {json_path.name}")
            return None
        
        all_text = []
        
        # Iterate through pages
        for page in data.get('pages', []):
            page_num = page.get('page', 'unknown')
            page_texts = []
            
            # Iterate through text regions in the page
            for region in page.get('textRegions', []):
                region_texts = []
                
                # ONLY use textLines, ignore the region-level text field
                # (the region-level text is often a duplicate or summary)
                for line in region.get('textLines', []):
                    if line.get('text'):
                        region_texts.append(line['text'])
                
                # Add region as a paragraph (separated by double newline)
                if region_texts:
                    page_texts.append('\n'.join(region_texts))
            
            # Add page separator (optional - comment out if not needed)
            if page_texts:
                all_text.append(f"=== Page {page_num} ===")
                # Separate regions with double newlines (paragraph breaks)
                all_text.append('\n\n'.join(page_texts))
        
        if all_text:
            raw_text = '\n'.join(all_text)
            # Apply text restoration processing
            processed_text = restore_text_lines(raw_text)
            return processed_text
        else:
            print(f"  Warning: No text found in {json_path.name}")
            return None
            
    except json.JSONDecodeError as e:
        print(f"  Error: Invalid JSON in {json_path}: {e}")
        return None
    except Exception as e:
        print(f"  Error processing {json_path}: {e}")
        return None


def process_newspapers(base_path='objects/newspapers'):
    """
    Process all JSON files in the newspapers directory.
    
    Args:
        base_path: Base path to the newspapers directory
    """
    base_path = Path(base_path)
    
    if not base_path.exists():
        print(f"Error: Directory '{base_path}' does not exist")
        return
    
    # Find all JSON files
    json_files = list(base_path.rglob('*.json'))
    
    if not json_files:
        print(f"No JSON files found in '{base_path}'")
        return
    
    print(f"Found {len(json_files)} JSON files to process\n")
    
    processed = 0
    skipped = 0
    errors = 0
    
    for json_path in json_files:
        # Generate output filename (remove _osd suffix if present)
        filename = json_path.stem  # Get filename without extension
        if filename.endswith('_osd'):
            filename = filename[:-4]  # Remove '_osd'
        
        txt_path = json_path.parent / f"{filename}.txt"
        
        # Skip if TXT file already exists (optional - comment out to overwrite)
        if txt_path.exists():
            print(f"Skipping {json_path.name} (TXT already exists)")
            skipped += 1
            continue
        
        print(f"Processing: {json_path.relative_to(base_path)}")
        
        # Extract and process text
        text = extract_text_from_json(json_path)
        
        if text:
            try:
                # Write to TXT file
                with open(txt_path, 'w', encoding='utf-8') as f:
                    f.write(text)
                print(f"  ✓ Created: {txt_path.name}")
                processed += 1
            except Exception as e:
                print(f"  ✗ Failed to write {txt_path}: {e}")
                errors += 1
        else:
            print(f"  ✗ No text extracted from {json_path.name}")
            errors += 1
        
        print()  # Blank line for readability
    
    # Summary
    print(f"{'='*60}")
    print(f"Processing complete!")
    print(f"Successfully processed: {processed}")
    print(f"Skipped: {skipped}")
    print(f"Errors: {errors}")
    print(f"{'='*60}")


if __name__ == "__main__":
    import sys
    
    # Allow custom base path as command line argument
    if len(sys.argv) > 1:
        base_path = sys.argv[1]
    else:
        base_path = 'objects/newspapers'
    
    print(f"Processing JSON files in: {base_path}\n")
    process_newspapers(base_path)