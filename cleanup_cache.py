#!/usr/bin/env python3
"""
Cache and Charts Cleanup Script for Finance Bro

This script cleans up temporary files from:
- ./cache/*.db (database cache files)
- ./exports/charts/*.png (generated chart images)
- ./exports/tearsheets/*.html (generated tearsheet reports)
- ./pandasai.log (PandasAI log file)

Usage:
    python cleanup_cache.py
"""

import sys
from pathlib import Path


def cleanup_directory(directory, file_pattern, description):
    """
    Clean up files matching a pattern in a directory.

    Args:
        directory (str): Directory path to clean
        file_pattern (str): File pattern to match (e.g., "*.png")
        description (str): Description for logging

    Returns:
        int: Number of files deleted
    """
    if not Path(directory).exists():
        print(f"📁 Directory {directory} does not exist, skipping...")
        return 0

    # Find files matching the pattern
    pattern_path = Path(directory) / file_pattern
    files_to_delete = list(pattern_path.parent.glob(file_pattern))

    if not files_to_delete:
        print(f"✅ No {description} found in {directory}")
        return 0

    deleted_count = 0
    for file_path in files_to_delete:
        try:
            Path(file_path).unlink()
            print(f"🗑️  Deleted: {file_path}")
            deleted_count += 1
        except OSError as e:
            print(f"❌ Error deleting {file_path}: {e}")

    print(f"✅ Cleaned up {deleted_count} {description} from {directory}")
    return deleted_count


def main():
    """Main cleanup function."""
    print("🧹 Finance Bro Cache & Charts Cleanup")
    print("=" * 40)

    # Get script directory as base path
    script_dir = Path(__file__).parent

    total_deleted = 0

    # Clean cache directory - *.db files
    cache_dir = script_dir / "cache"
    deleted = cleanup_directory(str(cache_dir), "*.db", "database cache files")
    total_deleted += deleted

    # Clean exports/charts directory - *.png files
    charts_dir = script_dir / "exports" / "charts"
    deleted = cleanup_directory(str(charts_dir), "*.png", "chart image files")
    total_deleted += deleted

    # Clean exports/tearsheets directory - *.html files
    tearsheets_dir = script_dir / "exports" / "tearsheets"
    deleted = cleanup_directory(str(tearsheets_dir), "*.html", "tearsheet HTML files")
    total_deleted += deleted

    # Clean pandasai.log file in project root
    deleted = cleanup_directory(str(script_dir), "pandasai.log", "PandasAI log file")
    total_deleted += deleted

    print("=" * 40)
    print(f"🎉 Cleanup complete! Total files deleted: {total_deleted}")

    if total_deleted == 0:
        print("💡 No files needed cleanup - directories are already clean!")
    else:
        print("✨ Cache, charts, tearsheets, and log files have been cleaned!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️  Cleanup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)
