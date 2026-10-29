# Automated File Organizer & Cleanup Utility

A Python command-line tool that tidies a cluttered folder (such as Downloads). It checks each file's extension, creates category subfolders as needed, and safely moves the files into them. It handles permission errors and duplicate file names, and logs everything it does.

## Features

- Sorts files into `Documents`, `Images`, `Videos`, `Archives` and `Code` folders using an extension-mapping dictionary
- Creates category folders only when they are needed
- Handles name collisions by renaming (`report.pdf` becomes `report (1).pdf`), so nothing is overwritten
- Catches `PermissionError`, `FileExistsError` and other `OSError`s, logs them and continues with the next file
- Leaves unknown file types, hidden files and partial downloads (`.crdownload`, `.part`, `.tmp`) untouched
- `--dry-run` mode to preview changes without moving anything
- Prints a formatted execution summary and writes a log to `organizer.log`

## Requirements

- Python 3 (uses only the standard library: `os`, `shutil`, `pathlib`, `logging`, `argparse`)

## Usage

Organize your Downloads folder (asks for confirmation first):

```
python organizer.py
```

Organize a specific folder:

```
python organizer.py "C:\Users\YourName\Desktop\MyFolder"
```

Preview only, without moving any files:

```
python organizer.py --dry-run
```

Skip the confirmation prompt:

```
python organizer.py --yes
```

## Supported categories

| Category | Extensions |
|----------|------------|
| Documents | .pdf .doc .docx .txt .rtf .odt .xls .xlsx .csv .ppt .pptx .md |
| Images | .jpg .jpeg .png .gif .bmp .svg .webp .tiff .ico |
| Videos | .mp4 .mkv .mov .avi .wmv .flv .webm |
| Archives | .zip .rar .7z .tar .gz .bz2 |
| Code | .py .js .html .css .java .c .cpp .h .json .xml .sql .ts .sh .ipynb |

To add or change a category, edit the `CATEGORIES` dictionary at the top of `organizer.py`.

## Example output

```
MOVED    report.pdf  ->  Documents/
MOVED    photo.JPG  ->  Images/
MOVED    notes.pdf  ->  Documents/  (renamed to notes (1).pdf)
SKIPPED  data.xyz  (unrecognized or temporary type)

========================================
EXECUTION SUMMARY
========================================
  Documents       2
  Images          1
----------------------------------------
  Total files relocated: 3
  Skipped (unknown type):   1
  Errors:                   0
========================================
```

## Files

| File | Description |
|------|-------------|
| `organizer.py` | Main script |
| `organizer.log` | Log of every action (created when the script runs) |

## Notes

- Test on a small folder first, or use `--dry-run`, before running on an important folder.
- Files inside existing subfolders are not touched; only files directly in the chosen folder are organized.
- Press Ctrl+C at any time to cancel.
