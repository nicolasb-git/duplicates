# Image Duplicate Detector

A powerful Python utility to find and group duplicate or near-duplicate images in a folder using perceptual hashing (`pHash`). It can identify images that have been resized, compressed, or converted to different formats.

## 🚀 Features

- **Perceptual Hashing**: Uses structural analysis to find similar images, not just exact byte-for-byte duplicates.
- **Smart Grouping**: Groups related images together and identifies a "Reference" version.
- **Similarity Scores**: Shows a percentage score for how closely a duplicate matches the reference.
- **Rich UI**: Beautiful terminal output with progress bars and formatted tables.
- **Fast Scanning**: Efficiently processes large directories with recursive support.
- **Wide Format Support**: Works with `.jpg`, `.jpeg`, `.png`, `.webp`, `.bmp`, and `.tiff`.

## 🛠️ Installation

1. **Clone or copy the files** to your local machine.
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## 📖 Usage

Run the script by providing the path to your image directory:

```bash
python3 main.py /path/to/your/images
```

### Options

| Flag | Description | Default |
|------|-------------|---------|
| `--threshold` | Sensitivity of the detection (lower is stricter) | `10` |
| `--recursive` | Scan subdirectories | `False` |

### Examples

**Strict detection (Exact duplicates):**
```bash
python3 main.py ./photos --threshold 2
```

**Loose detection (Find similar photos/burst shots):**
```bash
python3 main.py ./photos --threshold 15 --recursive
```

## 🔍 How it Works

The tool uses **Perceptual Hashing (pHash)** to create a 64-bit fingerprint of each image. Unlike standard file hashes (like MD5), perceptual hashes are:
1. **Resilient**: They stay the same if the image is resized or saved in a different format.
2. **Comparable**: You can measure the "distance" between two hashes to see how visually similar two images are.

### Understanding the Similarity Score
- **100%**: The images are structurally identical.
- **90%+**: Extremely similar, likely the same photo with different compression or tiny edits.
- **80%+**: Likely "burst" photos or photos of the same subject from a slightly different angle.

## 📦 Requirements
- Python 3.7+
- `Pillow` (Image processing)
- `ImageHash` (Perceptual hashing)
- `rich` (Terminal styling)
