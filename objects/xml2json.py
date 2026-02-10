import os
import json
import xml.etree.ElementTree as ET
import re

NS = {"pc": "http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15"}

PDF_RE = re.compile(r"(.*)\.pdf$", re.IGNORECASE)
XML_RE = re.compile(r"(.+)_P(\d+)\.xml$", re.IGNORECASE)

def parse_points(points):
    return [[int(x), int(y)] for x, y in 
            (p.split(",") for p in points.split())]

def parse_page_xml(xml_path, image_path, page_number):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    page_el = root.find(".//pc:Page", NS)
    
    page = {
        "page": page_number,
        "width": int(page_el.attrib["imageWidth"]),
        "height": int(page_el.attrib["imageHeight"]),
        "image": image_path,
        "annotations": []
    }
    
    for region in root.findall(".//pc:TextRegion", NS):
        coords = region.find("pc:Coords", NS)
        if coords is None:
            continue
        
        page["annotations"].append({
            "id": region.attrib.get("id"),
            "type": "TextRegion",
            "points": parse_points(coords.attrib["points"]),
            "text": ""
        })
        
        for line in region.findall("pc:TextLine", NS):
            coords = line.find("pc:Coords", NS)
            if coords is None:
                continue
            
            text_el = line.find(".//pc:TextEquiv/pc:Unicode", NS)
            text = text_el.text if text_el is not None else ""
            
            page["annotations"].append({
                "id": line.attrib.get("id"),
                "type": "TextLine",
                "points": parse_points(coords.attrib["points"]),
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
        
        # Extract folder name from base (e.g., "La_Vanguardia" from "La_Vanguardia_13-04-1944")
        folder_name = re.match(r"^(.+?)_\d", base).group(1)
        
        pages = []
        osd_tiles = []
        
        for page_num, xml_file in sorted(xmls[base]):
            xml_path = os.path.join(folder_path, xml_file)
            image_path = f"{folder_name}/images/{base}_page-{page_num}.jpg"
            
            page_data = parse_page_xml(xml_path, image_path, page_num)
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