import xml.etree.ElementTree as ET
from collections import defaultdict

def parse_diagram(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Map ID -> Component name
    id_to_name = {}
    edges = []

    for cell in root.iter("mxCell"):
        cell_id = cell.get("id")
        value = cell.get("value", "").strip()
        vertex = cell.get("vertex")
        edge = cell.get("edge")

        if vertex == "1":
            # It's a component (Frontend, Backend, etc.)
            id_to_name[cell_id] = value

        elif edge == "1":
            # It's an arrow/edge
            source = cell.get("source")
            target = cell.get("target")
            edges.append((source, target))

    # Build adjacency list
    adjacency = defaultdict(list)
    for src, tgt in edges:
        if src in id_to_name and tgt in id_to_name:
            adjacency[id_to_name[src]].append(id_to_name[tgt])

    return dict(adjacency)


if __name__ == "__main__":
    file_path = "foo.xml"  # replace with your XML file path
    adjacency_list = parse_diagram(file_path)

    print("Adjacency List:")
    for node, neighbors in adjacency_list.items():
        print(f"{node} -> {neighbors}")
