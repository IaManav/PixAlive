import os
import shutil

# Absolute paths
def model_or_video(type_):
    if type_=="model":
        src_folder = "/Users/karmansingh/Downloads/ScnLib"
        dst_folder = "/Users/karmansingh/Documents/ios Dev Projects/ARcademyFrames/ARcademyFrames/art.scnassets"

        # Ask for the file name (without .scn)
        file_name = input("Enter the image name (without extension): ").strip()
        src_path = os.path.join(src_folder, f"{file_name}.scn")
        dst_path = os.path.join(dst_folder, f"{file_name}.scn")
    elif type_=="video":
        src_folder = "/Users/karmansingh/Downloads/VideoRefImg"
        dst_folder = "/Users/karmansingh/Documents/ios Dev Projects/ARcademyFrames/ARcademyFrames"

        # Ask for the file name (without .scn)
        file_name = input("Enter the image name (without extension): ").strip()
        src_path = os.path.join(src_folder, f"{file_name}.mp4")
        dst_path = os.path.join(dst_folder, f"{file_name}.mp4")

    # Check if file exists before copying
    if not os.path.exists(src_path):
        print(f"❌ File not found at {src_path}")
    else:
        os.makedirs(dst_folder, exist_ok=True)
        shutil.copy(src_path, dst_path)
        print(f"✅ Successfully copied {src_path} → {dst_path}")