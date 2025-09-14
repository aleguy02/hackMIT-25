from scripts.parse_xml import parse_diagram
from scripts.normalize_component_types import normalize_component_types
from scripts.compose_templates import compose_config_factory
import yaml
import sys

fp = "test.drawio"  # replace with your XML file path
adjacency_json_str = parse_diagram(fp)
print("=== adj json str from parse_diagram ===")
print(adjacency_json_str)

obj = normalize_component_types(adjacency_json_str)
if not obj["success"]:
    print("NORMALIZE FAILED. EXITING")
    sys.exit()
print("=== normalized adj object from normalize_component_types ===")
print(obj["components"])

compose_conf = compose_config_factory(obj["components"])
print("=== normalized adj object from normalize_component_types ===")
print(compose_conf)

with open('yaml/compose.yaml', 'w') as f:
    yaml.dump(compose_conf, f, default_flow_style=False, indent=2)