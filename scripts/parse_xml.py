from re import A
import xml.etree.ElementTree as ET
from collections import defaultdict
import json

def _dict_to_escaped_json(adjacency: dict) -> str:
    # Convert the adjacency list to a JSON string
    json_str = json.dumps(adjacency)

    # Escape all double quotes with a backslash
    escaped_json_str = json_str.replace('"', '\\"')
    return escaped_json_str

def parse_diagram(file_path) -> str:
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

    # print(dict(adjacency))

    return _dict_to_escaped_json(adjacency)


# if __name__ == "__main__":
#     file_path = "foo.xml"  # replace with your XML file path
#     adjacency_jsonStr = parse_diagram(file_path)

#     print(adjacency_jsonStr)

