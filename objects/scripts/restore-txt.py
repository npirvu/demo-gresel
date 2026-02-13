import re
import sys
from pathlib import Path

def restore_text_lines(text):
    # Split by double newlines to get paragraphs
    paragraphs = text.split('\n\n\n')
    
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
    
    # Join paragraphs back with double newlines
    text = '\n\n\n'.join(restored_paragraphs)
        
    # Remove soft hyphens
    text = re.sub(r'¬\s*', '', text)
    
    # Fix double spaces
    text = re.sub(r'  +', ' ', text)
    
    return text

def process_file(input_file, output_file=None):
    input_path = Path(input_file)
    
    # Read input file
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            text = f.read()
    except UnicodeDecodeError:
        # Try with latin-1 if utf-8 fails
        with open(input_path, 'r', encoding='latin-1') as f:
            text = f.read()
            
    # Restore text
    restored_text = restore_text_lines(text)
    
    # Determine output file path
    if output_file is None:
        output_path = input_path.parent / f"{input_path.stem}_restored{input_path.suffix}"
    else:
        output_path = Path(output_file)
        
    # Write output file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(restored_text)
    print(f"Restored text saved to: {output_path}")
    return output_path

def main():
    if len(sys.argv) < 2:
        print("Usage: python restore_text.py <input_file> [output_file]")
        print("Example: python restore_text.py newspaper.txt")
        print("Example: python restore_text.py newspaper.txt restored.txt")
        sys.exit(1)
        
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    process_file(input_file, output_file)
    

if __name__ == "__main__":
    main()