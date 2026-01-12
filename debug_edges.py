import pandas as pd
import math

EDGE_FILE = "school-nav-data/edges_all.csv"
NODE_FILE = "school-nav-data/nodes/nodes_ground.csv"

def inspect_library_edges():
    # 1. Load Nodes to get ID of Senior Library
    df_nodes = pd.read_csv(NODE_FILE)
    lib_row = df_nodes[df_nodes['name'].str.contains("Senior Library", case=False, na=False)]
    
    if lib_row.empty:
        print("Senior Library node not found.")
        return

    lib_id = lib_row.iloc[0]['id']
    lib_x = lib_row.iloc[0]['x']
    lib_y = lib_row.iloc[0]['y']
    print(f"Senior Library ID: {lib_id} ({lib_x}, {lib_y})")

    # 2. Load Edges
    df_edges = pd.read_csv(EDGE_FILE)
    
    # Find edges connected to Library
    connected = df_edges[(df_edges['from'] == lib_id) | (df_edges['to'] == lib_id)]
    
    print(f"Found {len(connected)} edges connected to Senior Library.")
    
    for idx, row in connected.iterrows():
        other_id = row['to'] if row['from'] == lib_id else row['from']
        other_node = df_nodes[df_nodes['id'] == other_id].iloc[0]
        
        dist = math.hypot(lib_x - other_node['x'], lib_y - other_node['y'])
        print(f"Edge to {other_node['name']} ({other_id}): Dist={dist:.2f}, Accessible={row['accessible']}")
        print(f"   Coords: ({other_node['x']}, {other_node['y']})")

if __name__ == "__main__":
    inspect_library_edges()
