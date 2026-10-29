"""Automated File Organizer & Cleanup Utility.

Sorts the files in a folder (default: your Downloads folder) into category
subfolders such as Documents, Images, Videos, Archives and Code.

Usage:
    python organizer.py                  # organize ~/Downloads (asks to confirm)
    python organizer.py "C:\\some\\folder"  # organize a specific folder
    python organizer.py --dry-run        # preview only, moves nothing
    python organizer.py --yes            # skip the confirmation prompt

Files with unknown extensions are left where they are. Name collisions are
handled by renaming (report.pdf -> report (1).pdf). A log is written to
organizer.log inside the organized folder.
"""

import argparse
import logging
import os
import shutil
import sys
from pathlib import Path

CATEGORIES = {
    "Documents": {".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".xls", ".xlsx",
                  ".csv", ".ppt", ".pptx", ".md"},
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".tiff", ".ico"},
    "Videos": {".mp4", ".mkv", ".mov", ".avi", ".wmv", ".flv", ".webm"},
    "Archives": {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"},
    "Code": {".py", ".js", ".html", ".css", ".java", ".c", ".cpp", ".h", ".json",
             ".xml", ".sql", ".ts", ".sh", ".ipynb"},
}

# Flat extension -> category lookup, built from the dictionary above.
EXTENSION_MAP = {ext: cat for cat, exts in CATEGORIES.items() for ext in exts}

# Files that are still downloading or are temporary: never touch these.
SKIP_EXTENSIONS = {".crdownload", ".part", ".tmp", ".download"}
LOG_NAME = "organizer.log"


def setup_logging(folder):
    logger = logging.getLogger("organizer")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    fmt = logging.Formatter("%(asctime)s  %(levelname)-7s %(message)s", "%Y-%m-%d %H:%M:%S")
    try:
        file_handler = logging.FileHandler(folder / LOG_NAME, encoding="utf-8")
        file_handler.setFormatter(fmt)
        logger.addHandler(file_handler)
    except OSError:
        print("Warning: could not create log file; logging to console only.")
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(console)
    return logger


def unique_destination(dest_dir, name):
    """Return a path in dest_dir that does not exist yet (adds ' (1)', ' (2)'...)."""
    target = dest_dir / name
    if not target.exists():
        return target
    stem, suffix = Path(name).stem, Path(name).suffix
    counter = 1
    while True:
        target = dest_dir / f"{stem} ({counter}){suffix}"
        if not target.exists():
            return target
        counter += 1


def organize(folder, dry_run=False, logger=None):
    stats = {"moved": 0, "skipped": 0, "errors": 0}
    per_category = {}
    script_name = Path(__file__).name

    with os.scandir(folder) as entries:
        files = [e for e in entries if e.is_file(follow_symlinks=False)]

    for entry in files:
        name = entry.name
        ext = Path(name).suffix.lower()

        # Leave the script, the log, hidden files, partial downloads and unknown types.
        if name in (script_name, LOG_NAME) or name.startswith("."):
            continue
        if ext in SKIP_EXTENSIONS or ext not in EXTENSION_MAP:
            stats["skipped"] += 1
            logger.info(f"SKIPPED  {name}  (unrecognized or temporary type)")
            continue

        category = EXTENSION_MAP[ext]
        dest_dir = folder / category

        try:
            if dry_run:
                target = unique_destination(dest_dir, name)
                logger.info(f"WOULD MOVE  {name}  ->  {category}/{target.name}")
            else:
                dest_dir.mkdir(exist_ok=True)  # create the category folder on demand
                target = unique_destination(dest_dir, name)
                shutil.move(entry.path, str(target))
                note = "" if target.name == name else f"  (renamed to {target.name})"
                logger.info(f"MOVED    {name}  ->  {category}/{note}")
            stats["moved"] += 1
            per_category[category] = per_category.get(category, 0) + 1
        except PermissionError:
            stats["errors"] += 1
            logger.error(f"ERROR    {name}: permission denied (file may be open or protected)")
        except FileExistsError:
            stats["errors"] += 1
            logger.error(f"ERROR    {name}: a file with that name already exists")
        except OSError as exc:
            stats["errors"] += 1
            logger.error(f"ERROR    {name}: {exc}")

    return stats, per_category


def print_summary(stats, per_category, dry_run, logger):
    label = "would be moved" if dry_run else "relocated"
    line = "=" * 40
    logger.info("\n" + line)
    logger.info("EXECUTION SUMMARY" + ("  (DRY RUN)" if dry_run else ""))
    logger.info(line)
    for category in sorted(per_category):
        logger.info(f"  {category:<12}{per_category[category]:>5}")
    logger.info("-" * 40)
    logger.info(f"  Total files {label}: {stats['moved']}")
    logger.info(f"  Skipped (unknown type):   {stats['skipped']}")
    logger.info(f"  Errors:                   {stats['errors']}")
    logger.info(line)


def main():
    parser = argparse.ArgumentParser(description="Organize a folder into category subfolders.")
    parser.add_argument("folder", nargs="?", default=str(Path.home() / "Downloads"),
                        help="folder to organize (default: ~/Downloads)")
    parser.add_argument("--dry-run", action="store_true", help="preview without moving anything")
    parser.add_argument("--yes", action="store_true", help="skip the confirmation prompt")
    args = parser.parse_args()

    folder = Path(args.folder).expanduser().resolve()
    if not folder.is_dir():
        print(f"Error: '{folder}' is not a folder.")
        return 1

    print(f"Folder to organize: {folder}")
    if not args.dry_run and not args.yes:
        if input("Move files into category folders? (y/n): ").strip().lower() != "y":
            print("Cancelled. Nothing was moved.")
            return 0

    logger = setup_logging(folder)
    logger.info(f"Starting{' dry run' if args.dry_run else ''} on {folder}\n")
    stats, per_category = organize(folder, args.dry_run, logger)
    print_summary(stats, per_category, args.dry_run, logger)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (KeyboardInterrupt, EOFError):
        print("\nCancelled.")