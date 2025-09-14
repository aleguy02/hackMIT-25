from flask import Flask, request, render_template, jsonify, current_app
import os
import yaml
import uuid
from werkzeug.utils import secure_filename

from scripts.parse_xml import parse_diagram
from scripts.normalize_component_types import normalize_component_types
from scripts.compose_templates import compose_config_factory

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create artifacts directory
ARTIFACTS_DIR = os.path.join(os.getcwd(), 'artifacts')
if not os.path.exists(ARTIFACTS_DIR):
    os.makedirs(ARTIFACTS_DIR)

app.config['UPLOAD_FOLDER'] = ARTIFACTS_DIR

ALLOWED_EXTENSIONS = {'xml', 'drawio'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file selected'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if not allowed_file(file.filename):
            return jsonify({'error': 'Please upload a .xml or .drawio file'}), 400

        # === Generate unique job directory for artifacts ===
        JOB_DIR = os.path.join(app.config['UPLOAD_FOLDER'], str(uuid.uuid4()))
        os.makedirs(JOB_DIR)

        xml_filename = secure_filename(file.filename)
        fp = os.path.join(JOB_DIR, xml_filename)
        file.save(fp)

        adjacency_json_str = parse_diagram(fp)
        current_app.logger.debug(f"adjacency_json_str: {adjacency_json_str}")
        if adjacency_json_str == "{}":
            return jsonify({'error': 'Please include at least 2 component.'}), 400

        obj = normalize_component_types(adjacency_json_str)
        if not obj["success"]:
            return jsonify({'error': 'Please make sure all components are valid and try again.'}), 400
        current_app.logger.debug(f"components: {obj["components"]}")

        compose_conf = compose_config_factory(obj["components"])

        yaml_output = yaml.dump(compose_conf, default_flow_style=False, indent=2)
        # Also write the YAML output to a file in the job directory
        yaml_fp = os.path.join(JOB_DIR, 'compose.yaml')
        with open(yaml_fp, 'w') as f:
            f.write(yaml_output)
        
        # Success!
        return jsonify({
            'success': True,
            'compose_yaml': yaml_output
        })


    except Exception as e:
        current_app.logger.error(f"Exception occured (outer): {e}")
        return jsonify({'error': 'Please make sure all components are valid and try again.'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=False)