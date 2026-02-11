import os
import json
import xml.etree.ElementTree as ET
import re
from PIL import Image

NS = {"pc": "http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15"}

PDF_RE = re.compile(r"(.*)\.pdf$", re.IGNORECASE)
XML_RE = re.compile(r"(.+)_P(\d+)\.xml$", re.IGNORECASE)

def parse_points(points_str):
    """Convert points string to list of [x, y] coordinates"""
    return [[int(x), int(y)] for x, y in 
            (p.split(",") for p in points_str.split())]

def parse_text_equiv(element):
    """Extract text from TextEquiv element"""
    text_equiv = element.find("pc:TextEquiv", NS)
    if text_equiv is not None:
        unicode_el = text_equiv.find("pc:Unicode", NS)
        if unicode_el is not None and unicode_el.text:
            return unicode_el.text
    return ""

def parse_text_line(line_el, scale_x=1.0, scale_y=1.0):
    """Parse a TextLine element"""
    coords = line_el.find("pc:Coords", NS)
    if coords is None:
        return None
    
    points = parse_points(coords.attrib["points"])
    scaled_points = [[int(x * scale_x), int(y * scale_y)] for x, y in points]
    
    return {
        "id": line_el.attrib.get("id", ""),
        "type": "TextLine",
        "points": scaled_points,
        "text": parse_text_equiv(line_el)
    }

def parse_text_region(region_el, scale_x=1.0, scale_y=1.0):
    """Parse a TextRegion element with its contained TextLines"""
    coords = region_el.find("pc:Coords", NS)
    if coords is None:
        return None
    
    points = parse_points(coords.attrib["points"])
    scaled_points = [[int(x * scale_x), int(y * scale_y)] for x, y in points]
    
    # Parse the region itself
    region = {
        "id": region_el.attrib.get("id", ""),
        "type": "TextRegion",
        "points": scaled_points,
        "text": parse_text_equiv(region_el),
        "textLines": []
    }
    
    # Parse all TextLines within this region
    for line_el in region_el.findall("pc:TextLine", NS):
        line = parse_text_line(line_el, scale_x, scale_y)
        if line:
            region["textLines"].append(line)
    
    return region

def parse_page_xml(xml_path, image_path, page_number, actual_img_width=None, actual_img_height=None):
    """Parse PAGE XML file into structured JSON"""
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    page_el = root.find(".//pc:Page", NS)
    if page_el is None:
        raise ValueError(f"No Page element found in {xml_path}")
    
    xml_width = int(page_el.attrib["imageWidth"])
    xml_height = int(page_el.attrib["imageHeight"])
    
    # Calculate scale factors if actual dimensions provided
    scale_x = actual_img_width / xml_width if actual_img_width else 1.0
    scale_y = actual_img_height / xml_height if actual_img_height else 1.0
    
    page = {
        "page": page_number,
        "width": actual_img_width or xml_width,
        "height": actual_img_height or xml_height,
        "image": image_path,
        "textRegions": []
    }
    
    # Parse all TextRegions with their nested TextLines
    for region_el in page_el.findall("pc:TextRegion", NS):
        region = parse_text_region(region_el, scale_x, scale_y)
        if region:
            page["textRegions"].append(region)
    
    return page

def process_folder(folder_path):
    """Process all PDF/XML pairs in a folder"""
    files = os.listdir(folder_path)
    
    pdfs = {}
    xmls = {}
    
    for f in files:
        pdf_match = PDF_RE.match(f)
        xml_match = XML_RE.match(f)
        
        if pdf_match:
            base = pdf_match.group(1)
            pdfs[base] = f
            
        elif xml_match:
            base = xml_match.group(1)
            page = int(xml_match.group(2))
            xmls.setdefault(base, []).append((page, f))
    
    # Process each PDF that has XML files
    for base in pdfs:
        if base not in xmls:
            continue
        
        # Extract folder name (e.g., "La_Vanguardia" from "La_Vanguardia_13-04-1944")
        folder_name = re.match(r"^(.+?)_\d", base)
        if not folder_name:
            print(f"Warning: Could not extract folder name from {base}")
            continue
        
        pages = []
        osd_tiles = []
        
        # Process each page
        for page_num, xml_file in sorted(xmls[base]):
            xml_path = os.path.join(folder_path, xml_file)
            image_filename = f"{base}_page-{page_num}.jpg"
            image_path = f"objects/{folder_name}/images/{image_filename}"
            
            # Get actual image dimensions
            images_folder = os.path.join(os.path.dirname(folder_path), "images")
            full_image_path = os.path.join(images_folder, image_filename)
            
            actual_width, actual_height = None, None
            try:
                img = Image.open(full_image_path)
                actual_width, actual_height = img.width, img.height
                print(f"✓ Loaded {image_filename}: {actual_width}x{actual_height}")
            except Exception as e:
                print(f"⚠ Warning: Could not open {full_image_path}, using XML dimensions")
            
            # Parse the XML
            try:
                page_data = parse_page_xml(xml_path, image_path, page_num, actual_width, actual_height)
                pages.append(page_data)
                
                osd_tiles.append({
                    "type": "image",
                    "url": image_path,
                    "buildPyramid": True
                })
            except Exception as e:
                print(f"✗ Error parsing {xml_file}: {e}")
                continue
        
        if not pages:
            print(f"⚠ No pages generated for {base}")
            continue
        
        # Create output JSON
        output = {
            "id": base,
            "pages": pages,
            "tileSources": osd_tiles
        }
        
        out_path = os.path.join(folder_path, f"{base}_osd.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
            
        print(f"✓ Generated: {out_path}\n")

def main():
    ROOT = r"C:\Users\Nuria\Documents\GRESEL\repositorio\demo-gresel\objects"
    
    print("=" * 60)
    print("PAGE XML to JSON Converter")
    print("=" * 60)
    print()
    
    for root, dirs, files in os.walk(ROOT):
        # Only process folders that contain files
        if files:
            print(f"Processing: {root}")
            process_folder(root)

if __name__ == "__main__":
    main()