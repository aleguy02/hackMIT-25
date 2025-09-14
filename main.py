from scripts.parse_xml import parse_diagram
from scripts.normalize_component_types import normalize_component_types

fp = "foo.xml"  # replace with your XML file path
adjacency_json_str = parse_diagram(fp)
print(adjacency_json_str)

obj = normalize_component_types(adjacency_json_str)
print(obj)
