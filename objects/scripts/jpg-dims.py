from PIL import Image
import os

# Root folder
root_path = r"C:/Users/Nuria/Documents/GRESEL/repositorio/demo-gresel/objects"

print("Checking all images recursively...\n")

for root, dirs, files in os.walk(root_path):
    for filename in files:
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            img_path = os.path.join(root, filename)
            try:
                img = Image.open(img_path)
                relative_path = os.path.relpath(img_path, root_path)
                print(f"{relative_path}")
                print(f"  Size: {img.width} x {img.height}")
                print(f"XML says: 1601 x 2477")
                print(f"  Scale factor X: {img.width / 1601:.4f}")
                print(f"  Scale factor Y: {img.height / 2477:.4f}")
                print()
            except Exception as e:
                print(f"{filename} - Error: {e}\n")