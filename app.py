from flask import Flask, request, render_template, jsonify, current_app
import os
import tempfile
import yaml
from werkzeug.utils import secure_filename
from scripts.parse_xml import parse_diagram
from scripts.normalize_component_types import normalize_component_types
from scripts.compose_templates import compose_config_factory

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

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

        # Save uploaded file temporarily
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        try:
            adjacency_json_str = parse_diagram(filepath)
            current_app.logger.debug(f"adjacency_json_str: {adjacency_json_str}")
            if adjacency_json_str == "{}":
                return jsonify({'error': 'Please include at least 2 component.'}), 400

            obj = normalize_component_types(adjacency_json_str)
            if not obj["success"]:
                return jsonify({'error': 'Please make sure all components are valid and try again.'}), 400
            current_app.logger.debug(f"components: {obj["components"]}")

            compose_conf = compose_config_factory(obj["components"])

            yaml_output = yaml.dump(compose_conf, default_flow_style=False, indent=2)

            try:
                os.remove(filepath)
            except:
                pass

            return jsonify({
                'success': True,
                'compose_yaml': yaml_output
            })

        except Exception as e:
            current_app.logger.error(f"Exception occured (inner): {e}")
            try:
                os.remove(filepath)
            except:
                pass
            
            return jsonify({'error': 'Please make sure all components are valid and try again.'}), 500

    except Exception as e:
        current_app.logger.error(f"Exception occured (outer): {e}")
        return jsonify({'error': 'Please make sure all components are valid and try again.'}), 500

if __name__ == '__main__':
    app.run(debug=True)