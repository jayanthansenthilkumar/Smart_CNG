"""
Project Structure Visualizer
Shows the new OOP-organized structure
"""

import os
from pathlib import Path

def print_tree(directory, prefix="", max_depth=3, current_depth=0, exclude_dirs=None):
    """Print directory tree structure"""
    if exclude_dirs is None:
        exclude_dirs = {'__pycache__', '.git', 'instance', 'node_modules', '.venv', 'venv'}
    
    if current_depth >= max_depth:
        return
    
    try:
        entries = sorted(Path(directory).iterdir(), key=lambda x: (not x.is_dir(), x.name))
    except PermissionError:
        return
    
    for i, entry in enumerate(entries):
        if entry.name in exclude_dirs or entry.name.startswith('.'):
            continue
            
        is_last = i == len(entries) - 1
        current_prefix = "└── " if is_last else "├── "
        print(f"{prefix}{current_prefix}{entry.name}")
        
        if entry.is_dir():
            extension = "    " if is_last else "│   "
            print_tree(entry, prefix + extension, max_depth, current_depth + 1, exclude_dirs)

def main():
    print("=" * 70)
    print("Smart CNG - OOP Refactored Project Structure")
    print("=" * 70)
    print()
    
    project_root = Path(__file__).parent
    
    print("📁 Project Root:")
    print(f"   {project_root}")
    print()
    
    print("📂 Directory Structure:")
    print()
    print_tree(project_root, max_depth=3)
    
    print()
    print("=" * 70)
    print("Key Directories:")
    print("=" * 70)
    print()
    print("📦 core/              - NEW: OOP-based data models and services")
    print("  ├── data_models.py  - Data classes (CNGStation, Vehicle, etc.)")
    print("  ├── data_manager.py - Singleton data manager")
    print("  ├── base_services.py- Abstract base classes")
    print("  └── services.py     - Business logic services")
    print()
    print("📂 data/              - JSON data files (loaded by DataManager)")
    print("📂 models/            - SQLAlchemy database models")
    print("📂 services/          - Legacy services (redirects to core)")
    print("📂 templates/         - HTML templates")
    print("📂 static/            - CSS, JS, images")
    print()
    print("🚀 app_refactored.py  - NEW: Flask app with OOP services")
    print("📜 app.py             - Original app (backward compatibility)")
    print()
    
    # Count files
    core_files = len(list(Path(project_root / 'core').glob('*.py')))
    data_files = len(list(Path(project_root / 'data').glob('*.json')))
    
    print("=" * 70)
    print("Statistics:")
    print("=" * 70)
    print(f"Core Module Files: {core_files}")
    print(f"Data JSON Files: {data_files}")
    print(f"Total Services: 5 (consolidated from 8)")
    print(f"Data Model Classes: 6")
    print()

if __name__ == '__main__':
    main()
