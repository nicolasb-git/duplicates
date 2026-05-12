import os
import shutil
from pathlib import Path
from PIL import Image, ImageDraw
from detector import ImageDuplicateDetector

def create_test_images(test_dir: Path):
    if test_dir.exists():
        shutil.rmtree(test_dir)
    test_dir.mkdir()

    # Create original image
    img1 = Image.new('RGB', (100, 100), color=(73, 109, 137))
    d = ImageDraw.Draw(img1)
    d.text((10, 10), "Hello", fill=(255, 255, 0))
    img1.save(test_dir / "original.png")

    # Create exact duplicate (different format)
    img1.save(test_dir / "duplicate.jpg")

    # Create slightly modified image (resized)
    img1_resized = img1.resize((50, 50))
    img1_resized.save(test_dir / "resized.png")

    # Create different image
    img2 = Image.new('RGB', (100, 100), color=(255, 0, 0))
    d2 = ImageDraw.Draw(img2)
    d2.text((10, 10), "World", fill=(255, 255, 255))
    img2.save(test_dir / "different.png")

    print(f"Created test images in {test_dir}")

def verify():
    test_dir = Path("test_images")
    create_test_images(test_dir)

    detector = ImageDuplicateDetector(threshold=5)
    images = detector.find_images(str(test_dir))
    print(f"Found {len(images)} images")

    detector.compute_hashes(images)
    groups = detector.group_duplicates()

    print(f"Found {len(groups)} groups of duplicates")
    for i, group in enumerate(groups, 1):
        print(f"Group {i}: {[p.name for p in group]}")

    # Expected: original.png, duplicate.jpg, and resized.png should be grouped together
    # depending on threshold. With phash, resizing usually keeps the hash very similar.
    
    if len(groups) == 1 and len(groups[0]) >= 2:
        print("Verification SUCCESS: Duplicates detected correctly.")
    else:
        print("Verification FAILURE: Expected at least one group of duplicates.")

if __name__ == "__main__":
    verify()
