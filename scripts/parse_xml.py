from re import A
import xml.etree.ElementTree as ET
from collections import defaultdict
import json

def _dict_to_escaped_json(adjacency: dict) -> str:
    json_str = json.dumps(adjacency)

    escaped_json_str = json_str.replace('"', '\\"')
    return escaped_json_str

def parse_diagram(file_path) -> str:
    tree = ET.parse(file_path)
    root = tree.getroot()

    id_to_name = {}
    edges = []

    for cell in root.iter("mxCell"):
        cell_id = cell.get("id")
        value = cell.get("value", "").strip()
        vertex = cell.get("vertex")
        edge = cell.get("edge")

        if vertex == "1":
            id_to_name[cell_id] = value

        elif edge == "1":
            source = cell.get("source")
            target = cell.get("target")
            edges.append((source, target))
            edges.append((target, None))

    adjacency = defaultdict(list)
    for src, tgt in edges:
        if src in id_to_name and tgt in id_to_name:
            adjacency[id_to_name[src]].append(id_to_name[tgt])
        elif src in id_to_name and tgt is None:
            adjacency[id_to_name[src]] 


    return _dict_to_escaped_json(adjacency)
