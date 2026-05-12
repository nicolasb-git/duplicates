import sys
import argparse
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from detector import ImageDuplicateDetector

def main():
    parser = argparse.ArgumentParser(description="Detect duplicate images in a folder.")
    parser.add_argument("directory", type=str, help="Directory to scan for duplicates.")
    parser.add_argument("--threshold", type=int, default=10, help="Similarity threshold (lower is more strict). Default: 10")
    parser.add_argument("--recursive", action="store_true", help="Scan subdirectories recursively.")
    
    args = parser.parse_args()
    console = Console()

    if not os.path.isdir(args.directory):
        console.print(f"[bold red]Error:[/bold red] Directory '{args.directory}' does not exist.")
        sys.exit(1)

    detector = ImageDuplicateDetector(threshold=args.threshold)
    
    console.print(f"[bold blue]Scanning directory:[/bold blue] {args.directory}")
    images = detector.find_images(args.directory, recursive=args.recursive)
    
    if not images:
        console.print("[yellow]No images found in the specified directory.[/yellow]")
        return

    console.print(f"[green]Found {len(images)} images.[/green]")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    ) as progress:
        hash_task = progress.add_task("Computing hashes...", total=len(images))
        
        def update_progress(current, total):
            progress.update(hash_task, completed=current)
            
        detector.compute_hashes(images, progress_callback=update_progress)

    console.print("[bold blue]Finding duplicates...[/bold blue]")
    groups = detector.group_duplicates()

    if not groups:
        console.print("[bold green]No duplicates found![/bold green]")
        return

    console.print(f"[bold yellow]Found {len(groups)} groups of duplicates:[/bold yellow]")
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Group", justify="right", style="dim", width=6)
    table.add_column("File Path")
    table.add_column("Size (KB)", justify="right")
    table.add_column("Similarity", justify="right")

    for i, group in enumerate(groups, 1):
        for j, (path, distance) in enumerate(group):
            size_kb = os.path.getsize(path) / 1024
            
            # Calculate similarity percentage (64 is the hash length for phash)
            similarity = (1 - (distance / 64)) * 100
            sim_str = "Reference" if j == 0 else f"{similarity:.1f}%"
            
            table.add_row(
                str(i) if j == 0 else "",
                str(path),
                f"{size_kb:.1f}",
                sim_str
            )
        if i < len(groups):
            table.add_section()

    console.print(table)

if __name__ == "__main__":
    import os
    main()
