import pandas as pd
import os
import xml.etree.ElementTree as ET
import base64
import io
from PIL import Image

NODE_FILE = "school-nav-data/nodes/nodes_ground.csv"
SVG_FILE = "school-nav-data/svg/ground-level-nodes.svg"

def load_floor_image(svg_filename):
    """Parses SVG to find embedded base64 image and returns PIL Image and SVG dimensions."""
    path = os.path.join(SVG_DIR, svg_filename)
    if not os.path.exists(path):
        print(f"⚠️ Missing SVG {path}")
        return None, (1, 1)
    
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
    except Exception as e:
        print(f"Error parsing SVG {path}: {e}")
    return None, (1, 1)

SVG_DIR = "school-nav-data/svg"

def examine():
    print("--- Debugging Senior Library Wall Collision ---")
    
    # Load Nodes
    if not os.path.exists(NODE_FILE): 
        print(f"Node file not found: {NODE_FILE}")
        return
    df = pd.read_csv(NODE_FILE)
    
    # 1. Find Senior Library Node
    # Search for something like "Senior Library" or just "Library"
    lib_row = df[df['name'].str.contains("Senior Library", case=False, na=False)]
    if lib_row.empty:
        lib_row = df[df['name'].str.contains("Library", case=False, na=False)]
        
    if lib_row.empty:
        print("Could not find Senior Library node.")
        return

    start_node = lib_row.iloc[0].to_dict()
    print(f"Start Node: {start_node['name']} (id={start_node['id']}, x={start_node['x']}, y={start_node['y']})")

    # 2. Identify a Target Node "through the wall"
    # Looking at the map, Senior Library is top center. Auditorium is below it.
    # The erroneous path goes straight down.
    # Let's verify a node directly BELOW the library, e.g., with similar X but larger Y.
    # From map: Auditorium is roughly below.
    # Let's just pick a node with x ~ start_node['x'] and y > start_node['y'] + 100
    
    potential_targets = df[
        (df['x'] > start_node['x'] - 20) & 
        (df['x'] < start_node['x'] + 20) & 
        (df['y'] > start_node['y'] + 150)
    ]
    
    if potential_targets.empty:
        print("No direct vertical target found for testing.")
        # Just pick one far away to trace
        target_node = df.iloc[-1].to_dict()
    else:
        target_node = potential_targets.iloc[0].to_dict()
        
    print(f"Target Node: {target_node['name']} (id={target_node['id']}, x={target_node['x']}, y={target_node['y']})")
    
    # 3. Load Image and Check Collision Logic Trace
        
    img, svg_dim = load_floor_image("ground-level-nodes.svg")
    if not img:
        print("Failed to load image.")
        return
        
    svg_w, svg_h = svg_dim
    img_w, img_h = img.size
    scale_x = img_w / svg_w
    scale_y = img_h / svg_h
    print(f"Scale: {scale_x:.4f}, {scale_y:.4f} (Image: {img_w}x{img_h}, SVG: {svg_w}x{svg_h})")

    # Trace Check
    trace_collision(start_node, target_node, img, (scale_x, scale_y))

def trace_collision(a, b, image, scale):
    sx, sy = scale
    x1, y1 = int(a["x"] * sx), int(a["y"] * sy)
    x2, y2 = int(b["x"] * sx), int(b["y"] * sy)
    
    print(f"Checking Path in Pixels: ({x1}, {y1}) -> ({x2}, {y2})")
    
    w, h = image.size
    
    # Bresenham Points
    points = []
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    x, y = x1, y1
    x_inc = 1 if x1 < x2 else -1
    y_inc = 1 if y1 < y2 else -1
    
    # Simple step check for debugging (not full optimized bresenham but good enough for sample)
    steps = max(dx, dy)
    for i in range(steps + 1):
        progress = i / steps
        px = int(x1 + (x2 - x1) * progress)
        py = int(y1 + (y2 - y1) * progress)
        points.append((px, py))
        
    # Check brightness values along path
    dark_threshold = 100
    hits = 0
    consecutive = 0
    max_consecutive = 0
    
    pixels = image.load()
    
    print("Sampling first 10, middle 10, and last 10 pixels:")
    
    sample_indices = list(range(0, 10)) + \
                     list(range(len(points)//2 - 5, len(points)//2 + 5)) + \
                     list(range(len(points) - 10, len(points)))
                     
    min_bright = 255
    
    for i, (px, py) in enumerate(points):
        if 0 <= px < w and 0 <= py < h:
            val = pixels[px, py]
            if isinstance(val, tuple): brightness = sum(val[:3]) / 3
            else: brightness = val
            
            min_bright = min(min_bright, brightness)
            
            is_dark = brightness < dark_threshold
            if is_dark:
                consecutive += 1
                max_consecutive = max(max_consecutive, consecutive)
            else:
                consecutive = 0
            
            if i in sample_indices and 0 <= i < len(points):
                print(f"  [{i}]: ({px}, {py}) Val={val} Bright={brightness:.1f} {'DARK' if is_dark else ''}")
        else:
             if i in sample_indices:
                print(f"  [{i}]: ({px}, {py}) OUT OF BOUNDS")

    print(f"Path Analysis: Length={len(points)}")
    print(f"Min Brightness Found: {min_bright}")
    print(f"Max Consecutive Dark Pixels: {max_consecutive}")
    print(f"Collision (<100 thresh, >=3 consec)? {'YES' if max_consecutive >= 3 else 'NO'}")

if __name__ == "__main__":
    examine()
