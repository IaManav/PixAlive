# import os
# from PIL import Image
# import shutil
#
# # Absolute paths
# src_folder = "/Users/karmansingh/Downloads/Hori3dimages"
# dst_folder = "/Users/karmansingh/Documents/ios Dev Projects/MedVerseAI/MedVerseAI/Images"
#
# # Ask for the image file name (without extension)
# file_name = input("Enter the name of the image (without extension): ").strip()
#
# # Find the actual image file with any extension
# found_file = None
# for ext in [".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff", ".heic"]:
#     possible_path = os.path.join(src_folder, file_name + ext)
#     if os.path.exists(possible_path):
#         found_file = possible_path
#         break
#
# if not found_file:
#     print(f"❌ No image found with the name '{file_name}' in {src_folder}")
# else:
#     # Convert to PNG and save in the same folder temporarily
#     img = Image.open(found_file).convert("RGBA")
#     png_path = os.path.join(src_folder, f"{file_name}.png")
#     img.save(png_path, format="PNG", compress_level=0)  # High quality (no compression)
#
#     # Ensure destination exists
#     os.makedirs(dst_folder, exist_ok=True)
#
#     # Move to destination folder
#     dst_path = os.path.join(dst_folder, f"{file_name}.png")
#     shutil.move(png_path, dst_path)
#
#     print(f"✅ Converted and moved {file_name}.png → {dst_path}")


import os
import json
import shutil
from PIL import Image

HoriOrVer=input("Horizontal or vertical: ")
# --- Configuration ---
if HoriOrVer=="H":
    SRC_FOLDER = "/Users/karmansingh/Downloads/Hori3dimages"
    AR_RESOURCE_PATH = "/Users/karmansingh/Documents/ios Dev Projects/ARcademyFrames/ARcademyFrames/Assets.xcassets/horizontal3D.arresourcegroup"
elif HoriOrVer=="V":
    SRC_FOLDER = "/Users/karmansingh/Downloads/Vert3dimages"
    AR_RESOURCE_PATH = "/Users/karmansingh/Documents/ios Dev Projects/ARcademyFrames/ARcademyFrames/Assets.xcassets/vertical3d.arresourcegroup"
elif HoriOrVer=="VID":
    SRC_FOLDER = "/Users/karmansingh/Downloads/VideoRefImg"
    AR_RESOURCE_PATH = '/Users/karmansingh/Documents/ios Dev Projects/ARcademyFrames/ARcademyFrames/Assets.xcassets/VideoBaseImg.arresourcegroup'

# --- Input ---
image_name = input("Enter the image name (without extension): ").strip()
width_cm = float(input("Enter width in centimeters: ").strip())

# --- Step 1: Locate the source image ---
source_file = None
for ext in [".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff"]:
    possible_path = os.path.join(SRC_FOLDER, image_name + ext)
    if os.path.exists(possible_path):
        source_file = possible_path
        break

if not source_file:
    print(f"❌ No image found named '{image_name}' in {SRC_FOLDER}")
    exit()

# --- Step 2: Create target folder ---
target_dir_name = f"{image_name}.arreferenceimage"
target_dir_path = os.path.join(AR_RESOURCE_PATH, target_dir_name)
os.makedirs(target_dir_path, exist_ok=True)

# --- Step 3: Convert to PNG ---
converted_png_path = os.path.join(target_dir_path, f"{image_name}.png")
img = Image.open(source_file).convert("RGBA")
img.save(converted_png_path, format="PNG", compress_level=0)

# --- Step 4: Create Contents.json for the new folder ---
contents_data = {
    "images": [
        {
            "filename": f"{image_name}.png",
            "idiom": "universal"
        }
    ],
    "info": {
        "author": "xcode",
        "version": 1
    },
    "properties": {
        "unit": "centimeters",
        "width": width_cm
    }
}

with open(os.path.join(target_dir_path, "Contents.json"), "w") as f:
    json.dump(contents_data, f, indent=2)

# --- Step 5: Update root Contents.json ---
root_contents_path = os.path.join(AR_RESOURCE_PATH, "Contents.json")
if not os.path.exists(root_contents_path):
    print("⚠️ Root Contents.json not found, creating a new one.")
    root_data = {
        "info": {"author": "xcode", "version": 1},
        "resources": []
    }
else:
    with open(root_contents_path, "r") as f:
        root_data = json.load(f)

# Prevent duplicates
existing_files = [res["filename"] for res in root_data.get("resources", [])]
if f"{image_name}.arreferenceimage" not in existing_files:
    root_data["resources"].append({
        "filename": f"{image_name}.arreferenceimage"
    })

# Save updated root Contents.json
with open(root_contents_path, "w") as f:
    json.dump(root_data, f, indent=2)

print(f"Successfully added '{image_name}' as AR reference image.")
print(f"Path: {target_dir_path}")
print(f"Width: {width_cm} cm")