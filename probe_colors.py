import os
import xml.etree.ElementTree as ET
import base64
import io
from PIL import Image

SVG_DIR = "school-nav-data/svg"
SVG_FILE = "ground-level-nodes.svg"

def load_floor_image(svg_filename):
    path = os.path.join(SVG_DIR, svg_filename)
    if not os.path.exists(path): return None, (1, 1)
    try:
        tree = ET.parse(path)
        root = tree.getroot()
        viewbox = root.get('viewBox')
        svg_w, svg_h = 1000, 1000 
        if viewbox:
            parts = viewbox.split()
            if len(parts) == 4:
                svg_w = float(parts[2])
                svg_h = float(parts[3])
        else:
            w_str = root.get('width')
            h_str = root.get('height')
            if w_str and h_str:
                svg_w = float("".join(c for c in w_str if c.isdigit() or c == '.'))
                svg_h = float("".join(c for c in h_str if c.isdigit() or c == '.'))
        
        ns = {'svg': 'http://www.w3.org/2000/svg', 'xlink': 'http://www.w3.org/1999/xlink'}
        image_elem = root.find(".//svg:image", ns)
        if image_elem is None: image_elem = root.find(".//image")
        if image_elem is not None:
            href = image_elem.get(f"{{{ns['xlink']}}}href")
            if not href: href = image_elem.get('href')
            if href and href.startswith('data:image'):
                header, b64_data = href.split(',', 1)
                image_data = base64.b64decode(b64_data)
                img = Image.open(io.BytesIO(image_data))
                if img.mode not in ('RGB', 'L'): img = img.convert('RGB')
                return img, (svg_w, svg_h)
    except Exception: pass
    return None, (1, 1)

def probe():
    print("--- Probing Pixel Colors ---")
    img, svg_dim = load_floor_image(SVG_FILE)
    if not img:
        print("No image.")
        return
        
    svg_w, svg_h = svg_dim
    img_w, img_h = img.size
    sx = img_w / svg_w
    sy = img_h / svg_h
    
    # Senior Library roughly at (266, 117)
    # Target below at (~266, 280)
    # We trace a vertical line
    
    start_x, start_y = 266, 117
    end_x, end_y = 266, 280
    
    px1, py1 = int(start_x * sx), int(start_y * sy)
    px2, py2 = int(end_x * sx), int(end_y * sy)
    
    print(f"Sampling Vertical Line Pixels from ({px1}, {py1}) to ({px2}, {py2})")
    
    pixels = img.load()
    w, h = img.size
    
    darkest_val = 255
    darkest_coords = (0,0)
    
    # Just iterate Y
    for y in range(py1, py2 + 1):
        x = px1
        if 0 <= x < w and 0 <= y < h:
            val = pixels[x, y]
            if isinstance(val, tuple): brightness = sum(val[:3]) / 3
            else: brightness = val
            
            # Print significantly non-white pixels
            if brightness < 240:
                print(f"  Pixel ({x}, {y}): RGB={val} Brightness={brightness:.1f}")
                if brightness < darkest_val:
                    darkest_val = brightness
                    darkest_coords = (x, y)
    
    print(f"Darkest pixel found along line: {darkest_val} at {darkest_coords}")

if __name__ == "__main__":
    probe()
