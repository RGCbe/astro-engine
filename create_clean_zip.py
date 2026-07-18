import os
import zipfile
from pathlib import Path

def create_clean_zip(source_dir, output_filename):
    """Creates a ZIP file of the project containing only source code."""
    # Directories to completely ignore
    IGNORE_DIRS = {
        '.pytest_cache', '__pycache__', '.git', 'reports', 'artifacts',
        'engine_code_export', 'logs', 'local_backups', 'gemma_extractions',
        '.claude', 'scratch', 'readings', 'jadhagam', 'Books'
    }
    
    # Extensions to include
    INCLUDE_EXTS = {
        '.py', '.html', '.css', '.js', '.ts', '.tsx', '.json', '.md', '.txt', '.csv'
    }

    print(f"Creating {output_filename}...")
    
    with zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            # Mutate dirs in-place to skip ignored directories
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
            
            for file in files:
                file_path = Path(root) / file
                
                # Exclude specific files
                if file_path.suffix.lower() not in INCLUDE_EXTS:
                    continue
                if file_path.name.endswith('.pdf'):
                    continue
                    
                # Get path relative to the source_dir
                rel_path = file_path.relative_to(source_dir)
                
                # Add to ZIP
                zipf.write(file_path, arcname=rel_path)
                
    print(f"Successfully created {output_filename}")
    print(f"Size: {os.path.getsize(output_filename) / 1024 / 1024:.2f} MB")

if __name__ == "__main__":
    create_clean_zip(r"f:\astro", r"f:\astro\AstroReport_Clean_Source.zip")
