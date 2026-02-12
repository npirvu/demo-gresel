import re
import sys
from pathlib import Path

def restore_text_lines(text):
    lines = text.split('n')
    restored_lines = []
    
    for line in lines:
        # Strip whitespace
        line = line.strip()
        
        # Skip empty lines (preserve them)
        if not line:
            restored_lines.append(line)
            continue
        
        # Remove soft hyphens at end of lines followed by continuation
        line = re.sub(r'¬\s*', '', line)
        
        restored_lines.append(line)
    
    return '\n'.join(restored_lines)

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