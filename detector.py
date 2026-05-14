import os
import hashlib
import concurrent.futures
from pathlib import Path
from PIL import Image
import imagehash
from typing import List, Dict, Set, Tuple, Optional, Callable, DefaultDict
from collections import defaultdict

def _compute_md5(path: Path) -> Tuple[Path, Optional[str]]:
    """Helper function to compute MD5 hash of a file."""
    try:
        hash_md5 = hashlib.md5()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return path, hash_md5.hexdigest()
    except Exception:
        return path, None

def _compute_phash(path: Path) -> Tuple[Path, Optional[imagehash.ImageHash]]:
    """Helper function to compute pHash of an image."""
    try:
        with Image.open(path) as img:
            return path, imagehash.phash(img)
    except Exception:
        return path, None

class ImageDuplicateDetector:
    """
    Detects duplicate or near-duplicate images using perceptual hashing.
    """
    
    SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.webp', '.tiff', '.heic'}

    def __init__(self, threshold: int = 10):
        self.threshold = threshold
        self.hashes: Dict[Path, imagehash.ImageHash] = {}

    def find_images(self, directory: str, recursive: bool = True) -> List[Path]:
        """
        Finds all supported image files in the given directory (case-insensitive).
        """
        root = Path(directory)
        images = []
        
        all_files = root.rglob("*") if recursive else root.glob("*")
        
        for p in all_files:
            try:
                if p.is_file() and p.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                    images.append(p)
            except Exception:
                continue
                
        return sorted(list(set(images)))

    def compute_hashes(self, images: List[Path], progress_callback: Optional[Callable[[int, int], None]] = None):
        """
        Computes hashes for each image using an optimized two-step process:
        1. Fast MD5 check for exact duplicates.
        2. Perceptual hashing (pHash) only for unique images.
        """
        total = len(images)
        if total == 0:
            return

        # Step 1: Compute MD5 hashes in parallel
        md5_map: DefaultDict[str, List[Path]] = defaultdict(list)
        with concurrent.futures.ProcessPoolExecutor() as executor:
            md5_futures = [executor.submit(_compute_md5, path) for path in images]
            for future in concurrent.futures.as_completed(md5_futures):
                path, md5 = future.result()
                if md5:
                    md5_map[md5].append(path)
                else:
                    # If MD5 fails, treat as unique but we'll try pHash later
                    md5_map[f"fail_{path}"].append(path)

        # Step 2: Compute pHash only for one representative of each MD5 group
        representatives = [paths[0] for paths in md5_map.values()]
        unique_hashes: Dict[Path, imagehash.ImageHash] = {}
        
        processed_count = 0
        with concurrent.futures.ProcessPoolExecutor() as executor:
            phash_futures = [executor.submit(_compute_phash, path) for path in representatives]
            for future in concurrent.futures.as_completed(phash_futures):
                path, phash = future.result()
                if phash:
                    unique_hashes[path] = phash
                
                # Update progress based on how many files this representative covers
                # (approximate for smoother UI)
                processed_count += 1
                if progress_callback:
                    progress_callback(int((processed_count / len(representatives)) * total), total)

        # Step 3: Map pHashes back to all files (including exact duplicates)
        for md5, paths in md5_map.items():
            rep_path = paths[0]
            if rep_path in unique_hashes:
                ph = unique_hashes[rep_path]
                for p in paths:
                    self.hashes[p] = ph
        
        if progress_callback:
            progress_callback(total, total)

    def group_duplicates(self) -> List[List[Tuple[Path, int]]]:
        """
        Groups images that are within the similarity threshold.
        Returns a list of groups, where each group is a list of (Path, distance) tuples.
        """
        paths = list(self.hashes.keys())
        processed: Set[Path] = set()
        groups: List[List[Tuple[Path, int]]] = []

        for i, p1 in enumerate(paths):
            if p1 in processed:
                continue
            
            h1 = self.hashes[p1]
            current_group = [(p1, 0)]
            
            for p2 in paths[i+1:]:
                if p2 in processed:
                    continue
                
                h2 = self.hashes[p2]
                distance = h1 - h2
                if distance <= self.threshold:
                    current_group.append((p2, int(distance)))
                    processed.add(p2)
            
            if len(current_group) > 1:
                groups.append(current_group)
                processed.add(p1)

        return groups
