import os
from pathlib import Path
from PIL import Image
import imagehash
from collections import defaultdict
from typing import List, Dict, Set, Tuple, Optional, Callable

class ImageDuplicateDetector:
    """
    Detects duplicate or near-duplicate images using perceptual hashing.
    """
    
    SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.webp', '.tiff'}

    def __init__(self, threshold: int = 10):
        self.threshold = threshold
        self.hashes: Dict[Path, imagehash.ImageHash] = {}

    def find_images(self, directory: str, recursive: bool = True) -> List[Path]:
        """
        Finds all supported image files in the given directory (case-insensitive).
        """
        root = Path(directory)
        images = []
        
        # Walk through files and filter by lowercase extension
        all_files = root.rglob("*") if recursive else root.glob("*")
        
        for p in all_files:
            try:
                if p.is_file() and p.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                    images.append(p)
            except Exception:
                # Handle potential permission errors or broken symlinks
                continue
                
        return sorted(list(set(images)))

    def compute_hashes(self, images: List[Path], progress_callback: Optional[Callable[[int, int], None]] = None):
        """
        Computes phash for each image.
        """
        total = len(images)
        for i, path in enumerate(images):
            try:
                with Image.open(path) as img:
                    h = imagehash.phash(img)
                    self.hashes[path] = h
            except Exception as e:
                # Skip unreadable images
                pass
            
            if progress_callback:
                progress_callback(i + 1, total)

    def group_duplicates(self) -> List[List[Tuple[Path, int]]]:
        """
        Groups images that are within the similarity threshold.
        Returns a list of groups, where each group is a list of (Path, distance) tuples.
        The distance is relative to the first image in the group.
        """
        paths = list(self.hashes.keys())
        processed: Set[Path] = set()
        groups: List[List[Tuple[Path, int]]] = []

        for i, p1 in enumerate(paths):
            if p1 in processed:
                continue
            
            h1 = self.hashes[p1]
            current_group = [(p1, 0)]  # Reference image has distance 0
            
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
