import os
import json
import xml.etree.ElementTree as ET
import re
from PIL import Image

NS = {"pc": "http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15"}

PDF_RE = re.compile(r"(.*)\.pdf$", re.IGNORECASE)
XML_RE = re.compile(r"(.+)_P(\d+)\.xml$", re.IGNORECASE)

def parse_points(points):
    return [[int(x), int(y)] for x, y in 
            (p.split(",") for p in points.split())]

def parse_page_xml(xml_path, image_path, page_number, actual_img_width=None, actual_img_height=None):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    page_el = root.find(".//pc:Page", NS)
    
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
        "annotations": []
    }
    
    for region in root.findall(".//pc:TextRegion", NS):
        coords = region.find("pc:Coords", NS)
        if coords is None:
            continue
        
        # Scale the points
        points = parse_points(coords.attrib["points"])
        scaled_points = [[int(x * scale_x), int(y * scale_y)] for x, y in points]
        
        page["annotations"].append({
            "id": region.attrib.get("id"),
            "type": "TextRegion",
            "points": scaled_points,
            "text": ""
        })
        
        for line in region.findall("pc:TextLine", NS):
            coords = line.find("pc:Coords", NS)
            if coords is None:
                continue
            
            text_el = line.find(".//pc:TextEquiv/pc:Unicode", NS)
            text = text_el.text if text_el is not None else ""
            
            # Scale the points
            points = parse_points(coords.attrib["points"])
            scaled_points = [[int(x * scale_x), int(y * scale_y)] for x, y in points]
            
            page["annotations"].append({
                "id": line.attrib.get("id"),
                "type": "TextLine",
                "points": scaled_points,
                "text": text
            })
            
    return page

def process_folder(folder_path):
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
            
    for base in pdfs:
        if base not in xmls:
            continue
        
        folder_name_raw = re.match(r"^(.+?)_\d", base).group(1)
        folder_name = folder_name_raw.replace("_", "-")
        
        pages = []
        osd_tiles = []
        
        for page_num, xml_file in sorted(xmls[base]):
            xml_path = os.path.join(folder_path, xml_file)
            image_filename = f"{base}_page-{page_num}.jpg"
            image_path = f"objects/{folder_name}/images/{image_filename}"
            
            # Images are in parent folder's images directory, not in the date folder
            images_folder = os.path.join(os.path.dirname(folder_path), "images")
            full_image_path = os.path.join(images_folder, image_filename)
            
            try:
                img = Image.open(full_image_path)
                actual_width, actual_height = img.width, img.height
                print(f"Loaded {image_filename}: {actual_width}x{actual_height}")
            except Exception as e:
                print(f"Warning: Could not open {full_image_path}, using XML dimensions - {e}")
                actual_width, actual_height = None, None
            
            page_data = parse_page_xml(xml_path, image_path, page_num, actual_width, actual_height)
            pages.append(page_data)
            
            osd_tiles.append({
                "type": "image",
                "url": image_path,
                "buildPyramid": True
            })
        
        output = {
            "id": base,
            "pages": pages,
            "tileSources": osd_tiles
        }
        
        out_path = os.path.join(folder_path, f"{base}_osd.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
            
        print(f"Generated: {out_path}")
        

ROOT = r"C:\Users\Nuria\Documents\GRESEL\repositorio\demo-gresel\objects"

for root, dirs, files in os.walk(ROOT):
    process_folder(root)