import os
import sys
from PIL import Image, ImageOps
from concurrent.futures import ProcessPoolExecutor

QUALITY = 15
EXTENSIONS = (".jpg", ".jpeg", ".png")


def convert_to_webp(input_path, output_path):
    with Image.open(input_path) as img:
        img = ImageOps.exif_transpose(img)

        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGBA" if "A" in img.mode else "RGB")

        img.save(
            output_path,
            "WEBP",
            quality=QUALITY,
            method=6,
            optimize=True
        )


def worker(job):
    input_path, output_path = job

    try:
        if os.path.exists(output_path):
            return f"Skipped (exists): {os.path.basename(input_path)}"

        convert_to_webp(input_path, output_path)

        original = os.path.getsize(input_path)
        compressed = os.path.getsize(output_path)
        reduction = 100 * (1 - compressed / original)

        return f"Converted: {os.path.basename(input_path)} ({reduction:.1f}% saved)"

    except Exception as e:
        return f"Error: {input_path} -> {e}"


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))

    jobs = []

    # Collect all image jobs
    for root, dirs, files in os.walk(script_dir):

        # Prevent re-processing output folders
        if "WebP" in dirs:
            dirs.remove("WebP")

        image_files = [f for f in files if f.lower().endswith(EXTENSIONS)]
        if not image_files:
            continue

        output_dir = os.path.join(root, "WebP")
        os.makedirs(output_dir, exist_ok=True)

        for filename in image_files:
            input_path = os.path.join(root, filename)
            output_path = os.path.join(
                output_dir,
                os.path.splitext(filename)[0] + ".webp"
            )

            jobs.append((input_path, output_path))

    print(f"Found {len(jobs)} images\n")

    # Use multiple CPU cores
    workers = min(8, os.cpu_count() or 4)

    with ProcessPoolExecutor(max_workers=workers) as executor:
        for result in executor.map(worker, jobs):
            print(result)

    print("\nDone!")


if __name__ == "__main__":
    main()