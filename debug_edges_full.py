import pandas as pd
import math
import os
import xml.etree.ElementTree as ET
import base64
import io
from PIL import Image

EDGE_FILE = "school-nav-data/edges_all.csv"
NODE_FILE = "school-nav-data/nodes/nodes_ground.csv"
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

def has_collision(a, b, image, scale=(1, 1)):
    if image is None: return False
    sx, sy = scale
    x1, y1 = int(a["x"] * sx), int(a["y"] * sy)
    x2, y2 = int(b["x"] * sx), int(b["y"] * sy)
    
    w, h = image.size
    # Bounds check
    if (x1 < 0 or x1 >= w or y1 < 0 or y1 >= h) and (x2 < 0 or x2 >= w or y2 < 0 or y2 >= h):
        return False

    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    steep = abs(dy) > abs(dx)
    if steep: x1, y1, x2, y2 = y1, x1, y2, x2
    if x1 > x2: x1, y1, x2, y2 = x2, y1, y2, y1
        
    dx = x2 - x1
    dy = abs(y2 - y1)
    error = dx / 2.0
    ystep = 1 if y1 < y2 else -1
    y = y1
    
    path_pixels = []
    for x in range(x1, x2 + 1):
        coord = (y, x) if steep else (x, y)
        path_pixels.append(coord)
        error -= dy
        if error < 0:
            y += ystep
            error += dx

    margin = 5
    if len(path_pixels) <= margin * 2: check_pixels = path_pixels
    else: check_pixels = path_pixels[margin:-margin]
        
    consecutive_hits = 0
    DARK_THRESHOLD = 160 
    pixels = image.load()
    
    for px, py in check_pixels:
        if 0 <= px < w and 0 <= py < h:
            val = pixels[px, py]
            if isinstance(val, tuple): brightness = sum(val[:3]) / 3
            else: brightness = val
            
            if brightness < DARK_THRESHOLD:
                consecutive_hits += 1
                if consecutive_hits >= 3: return True
            else:
                consecutive_hits = 0
    return False

def analyze():
    print("--- Analyzing Edges from Senior Library ---")
    
    # Load Image
    img, svg_dim = load_floor_image(SVG_FILE)
    if img:
        svg_w, svg_h = svg_dim
        img_w, img_h = img.size
        scale = (img_w / svg_w, img_h / svg_h)
        print(f"Image Loaded. Scale: {scale}")
    else:
        print("Image failed to load.")
        return

    # Load Nodes
    df_nodes = pd.read_csv(NODE_FILE)
    lib_row = df_nodes[df_nodes['name'].str.contains("Senior Library", case=False, na=False)]
    if lib_row.empty: return
    lib_node = lib_row.iloc[0].to_dict()
    lib_id = lib_node['id']
    
    # Load Edges
    df_edges = pd.read_csv(EDGE_FILE)
    connected = df_edges[(df_edges['from'] == lib_id) | (df_edges['to'] == lib_id)]
    
    print(f"Edges found: {len(connected)}")
    
    for idx, row in connected.iterrows():
        other_id = row['to'] if row['from'] == lib_id else row['from']
        other_row = df_nodes[df_nodes['id'] == other_id]
        if other_row.empty: continue
        other_node = other_row.iloc[0].to_dict()
        
        dist = math.hypot(lib_node['x'] - other_node['x'], lib_node['y'] - other_node['y'])
        collision = has_collision(lib_node, other_node, img, scale)
        
        print(f"Edge to {other_node['name']} ({other_id}):")
        print(f"  Dist: {dist:.2f}")
        print(f"  Collision Detected? {collision}")
        
        if collision:
            print("  [BUG] This edge exists in CSV but HAS COLLISION!")

if __name__ == "__main__":
    analyze()
