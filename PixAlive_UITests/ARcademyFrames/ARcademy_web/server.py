from flask import Flask, render_template, request, jsonify, send_from_directory, abort
import os
import uuid
from werkzeug.utils import secure_filename
import subprocess
import json
import shutil
from PIL import Image


application = Flask(__name__)
app = application

UPLOAD_FOLDER = 'static/uploads'
MODEL_FOLDER = '../ARcademyFrames/art.scnassets'
VIDEO_FOLDER = '../ARcademyFrames'

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', "webp", "bmp", "tiff"}
ALLOWED_MODEL_EXTENSIONS = {'scn'}
ALLOWED_VIDEO_EXTENSIONS = {'mp4'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MODEL_FOLDER'] = MODEL_FOLDER
app.config['VIDEO_FOLDER'] = VIDEO_FOLDER


def allowed_file(filename, allowed_ext):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_ext


@app.route('/', methods=['GET'])
def home():
    return render_template('form.html')

@app.route('/marketplace',methods=["GET","Post"])
def marketplace():
    return render_template("marketPlace2.html")

@app.route('/download/<model_name>')
def download_model(model_name):
    filename = f"{model_name}.scn"
    model_dir = os.path.join(app.static_folder, '3dModels')

    # Check if file exists
    file_path = os.path.join(model_dir, filename)
    if not os.path.exists(file_path):
        abort(404, description=f"Model '{filename}' not found.")

    # Send file for download
    return send_from_directory(model_dir, filename, as_attachment=True)

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/upload', methods=['GET', 'POST'])
def upload_image():
    if 'image' not in request.files:
        return "No image file part", 400

    image_file = request.files['image']
    model_file = request.files['output_type_filed']
    video_file = request.files['output_type_filev']

    if image_file.filename == '':
        return "No selected image", 400

    # Ensure directories exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(MODEL_FOLDER, exist_ok=True)
    os.makedirs(VIDEO_FOLDER, exist_ok=True)
    name_=uuid.uuid4().hex
    if request.form.get('output_type') == '3D Model':
        model_file = request.files.get('output_type_filed')
        if model_file and model_file.filename and allowed_file(model_file.filename, ALLOWED_MODEL_EXTENSIONS):
            filename = model_file.filename
            if '.' in filename:
                ext = filename.rsplit('.', 1)[1].lower()
            else:
                ext = 'dat'  # fallback extension
            unique_filename2 = f"{name_}.{ext}"
            model_path = os.path.join(MODEL_FOLDER, unique_filename2)
            model_file.save(model_path)
            model_path = f"../ARcademyFrames/art.scnassets/{name_}.scn"
            subprocess.run(["xcrun", "swift", "ExpAdding.swift", model_path], check=True)
    elif request.form.get('output_type') == 'Video Design':
        video_file = request.files.get('output_type_filev')
        if video_file and video_file.filename and allowed_file(video_file.filename, ALLOWED_VIDEO_EXTENSIONS):
            # filename = video_file.filename
            ext = "mp4"
            unique_filename1 = f"{name_}.{ext}"
            video_path = os.path.join(app.config['VIDEO_FOLDER'], unique_filename1)
            video_file.save(video_path)

    #     # Save video file if uploaded and allowed

    # Save image file
    if allowed_file(image_file.filename, ALLOWED_EXTENSIONS):
        # Get extension and save uploaded image
        ext = image_file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{name_}.{ext}"
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        image_file.save(image_path)

        # Get form inputs
        width = request.form.get('width')
        output_type = request.form.get('output_type')
        display_orientation = request.form.get('display_orientation')

        # Debug print
        print(
            f"ext = {ext}, "
            f"unique_filename = {unique_filename}, "
            f"image_path = {image_path}, "
            f"image_file = {image_file}, "
            f"width = {width}, "
            f"output_type = {output_type}, "
            f"display_orientation = {display_orientation}"
        )

        # Select destination AR group path
        if output_type == "3D Model" and display_orientation == "Horizontal Table":
            PaTh = "../ARcademyFrames/Assets.xcassets/horizontal3D.arresourcegroup"
        elif output_type == "3D Model" and display_orientation == "Vertical Wall":
            PaTh = "../ARcademyFrames/Assets.xcassets/vertical3d.arresourcegroup"
        elif output_type == "Video Design":
            PaTh = "../ARcademyFrames/Assets.xcassets/VideoBaseImg.arresourcegroup"
        else:
            print("❌ Invalid output type or display orientation.")
            return "Invalid selection", 400

        # ✅ The uploaded file itself is now the source
        source_file = image_path

        # Make target directory
        target_dir_name = f"{name_}.arreferenceimage"
        target_dir_path = os.path.join(PaTh, target_dir_name)
        os.makedirs(target_dir_path, exist_ok=True)

        # Convert to PNG with original quality
        converted_png_path = os.path.join(target_dir_path, f"{name_}.png")
        img = Image.open(source_file).convert("RGBA")
        img.save(converted_png_path, format="PNG", compress_level=0)

        # Create Contents.json inside the reference image folder
        contents_data = {
            "images": [
                {
                    "filename": f"{name_}.png",
                    "idiom": "universal"
                }
            ],
            "info": {
                "author": "xcode",
                "version": 1
            },
            "properties": {
                "unit": "centimeters",
                "width": float(width)
            }
        }

        with open(os.path.join(target_dir_path, "Contents.json"), "w") as f:
            json.dump(contents_data, f, indent=2)

        # Update (or create) root Contents.json
        root_contents_path = os.path.join(PaTh, "Contents.json")
        if not os.path.exists(root_contents_path):
            print("⚠️ Root Contents.json not found, creating a new one.")
            root_data = {
                "info": {"author": "xcode", "version": 1},
                "resources": []
            }
        else:
            with open(root_contents_path, "r") as f:
                root_data = json.load(f)

        existing_files = [res["filename"] for res in root_data.get("resources", [])]
        if f"{name_}.arreferenceimage" not in existing_files:
            root_data["resources"].append({
                "filename": f"{name_}.arreferenceimage"
            })

        with open(root_contents_path, "w") as f:
            json.dump(root_data, f, indent=2)

        print(f"✅ Successfully added '{name_}' as AR reference image.")
        print(f"📂 Path: {target_dir_path}")
        print(f"📏 Width: {width} cm")

        return render_template('success.html',
                               width=width,
                               output_type=output_type,
                               display_orientation=display_orientation,
                               filename=unique_filename)

    return "File type not allowed", 400


if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(MODEL_FOLDER, exist_ok=True)
    os.makedirs(VIDEO_FOLDER, exist_ok=True)
#    app.run(host="127.0.0.1", port=5000, debug=True)
     app.run(host="172.20.10.2",debug=True,port=3852)
