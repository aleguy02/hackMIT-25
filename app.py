from flask import Flask, request, render_template, jsonify, redirect, url_for
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

        # Process the pipeline
        try:
            # Step 1: Parse XML diagram
            adjacency_json_str = parse_diagram(filepath)

            # Step 2: Normalize component types using Claude API
            obj = normalize_component_types(adjacency_json_str)
            if not obj["success"]:
                return jsonify({'error': 'Please make sure all components are valid and try again.'}), 400

            # Step 3: Generate compose configuration
            compose_conf = compose_config_factory(obj["components"])

            # Convert to YAML string
            yaml_output = yaml.dump(compose_conf, default_flow_style=False, indent=2)

            # Clean up temporary file
            try:
                os.remove(filepath)
            except:
                pass

            return jsonify({
                'success': True,
                'compose_yaml': yaml_output
            })

        except Exception as e:
            # Clean up temporary file
            try:
                os.remove(filepath)
            except:
                pass

            # Return generic error message for Claude API failures or other errors
            return jsonify({'error': 'Please make sure all components are valid and try again.'}), 500

    except Exception as e:
        return jsonify({'error': 'Please make sure all components are valid and try again.'}), 500

if __name__ == '__main__':
    app.run(debug=True)