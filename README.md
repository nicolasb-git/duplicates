# Image Duplicate Detector

A high-performance Python utility to find and group duplicate or near-duplicate images in a folder using perceptual hashing (`pHash`). It can identify images that have been resized, compressed, or converted to different formats.

## 🚀 Key Features

- **High Performance**: Uses **Multiprocessing** to utilize all available CPU cores for lightning-fast scanning.
- **Exact-Match Fast Path**: Uses **MD5 hashing** to instantly identify byte-for-byte identical files, skipping expensive image processing for known duplicates.
- **Smart Grouping**: Groups related images together and identifies a "Reference" version.
- **Similarity Scores**: Shows a percentage score for how closely a duplicate matches the reference.
- **Wide Format Support**: Works with `.jpg`, `.jpeg`, `.png`, `.webp`, `.bmp`, `.tiff`, and **.heic** (iPhone photos).
- **Case Insensitive**: Automatically finds images regardless of extension case (e.g., `.jpg`, `.JPG`, `.jPeG`).
- **Terminal Friendly**: Outputs absolute paths that are **clickable links** in most modern terminals.

## 🛠️ Installation

1. **Clone or copy the files** to your local machine.
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## 📖 Usage

### Option 1: Direct Python
```bash
python3 main.py [directory]
```

### Option 2: MacOS Script (Convenience)
I have included a shell script `img-dedup` that allows you to run the tool from anywhere.

1. **Make it globally accessible**:
   ```bash
   sudo ln -s "/Users/kaerith/workspace/duplicates/img-dedup" /usr/local/bin/img-dedup
   ```

2. **Run it from anywhere**:
   ```bash
   img-dedup [directory] --threshold 10 --recursive
   ```

*Note: If no directory is provided, it defaults to the current directory (`.`)*

### Options

| Flag | Description | Default |
|------|-------------|---------|
| `--threshold` | Sensitivity of the detection (lower is stricter) | `10` |
| `--recursive` | Scan subdirectories | `False` |

## 🔍 How it Works

The tool uses a multi-stage analysis:
1. **MD5 Pass**: Instantly groups exact byte-for-byte duplicates.
2. **Perceptual Pass**: For unique images, it uses **Perceptual Hashing (pHash)** to create a visual fingerprint.
3. **Comparison**: Measures the "Hamming distance" between fingerprints to find visual matches.

### Understanding the Similarity Score
- **100%**: The images are structurally identical (even if file formats differ).
- **90%+**: Extremely similar, likely the same photo with different compression.
- **80%+**: Likely "burst" photos or similar shots of the same subject.

## 📦 Requirements
- Python 3.7+
- `Pillow`
- `ImageHash`
- `rich`
