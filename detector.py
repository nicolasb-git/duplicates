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
        Finds all supported image files in the given directory.
        """
        path = Path(directory)
        images = []
        
        patterns = ["*" + ext for ext in self.SUPPORTED_EXTENSIONS]
        
        for pattern in patterns:
            if recursive:
                images.extend(path.rglob(pattern))
            else:
                images.extend(path.glob(pattern))
                
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
