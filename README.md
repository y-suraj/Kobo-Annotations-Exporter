# Kobo Annotations Exporter

A local desktop application that turns Kobo highlights and typed notes into clean, browser-ready HTML notebooks.

Export individual books or combine selected books, copy your highlights, create shareable quote images, and read your exported notes in light or dark mode.

## Features

### Annotation export

- Read annotations from `KoboReader.sqlite`.
- Select the `.kobo` folder or Kobo drive root.
- Search annotated books by title or author.
- Select one or multiple books.
- Export separate HTML files for selected books by default.
- Optionally combine selected books into one HTML notebook.
- Include book titles, authors, highlights, typed notes, and available chapter information.
- Export standalone notes, even when they have no highlighted text.
- Browse combined exports using a clickable table of contents.

### Reading and copying

- Open exported notebooks offline in a browser.
- Switch between light and dark mode.
- Copy individual highlights or notes.
- Print notebooks or save them as PDF using the browser.
- Keep print output light even when viewing the notebook in dark mode.

### Quote images

- Turn a highlight or note into a square 1080 × 1080 PNG.
- Choose a custom background colour.
- Automatically adjust text colour for contrast.
- Optionally include the book name, author name, or both.
- Keep book and author attribution off by default.
- Wrap text at word or dash boundaries.
- Copy the image to the clipboard or download it as a PNG.

### Local processing

- No application account or cloud service required.
- Annotation extraction and image generation happen locally.
- The Kobo database is opened read-only.
- Windows executable builds can run without a separate Python installation.

## Getting started

### Option 1: Windows executable

If a packaged build is available:

1. Obtain `Kobo_Annotations_Exporter.exe` from the project maintainer or a published GitHub release.
2. Save it to a folder on your computer.
3. Double-click it to start the application.

You do not need Python, the source files, or a separate icon file to run the packaged executable.

The executable must be compatible with your Windows version and processor architecture. New or unsigned builds may trigger Windows security warnings. Verify the source and scan downloaded files before running them.

### Option 2: Run from source

Requirements:

- Python 3.9 or newer.
- Tkinter support in your Python installation.

The application itself uses Python's standard library; no third-party runtime packages are required.

Open a terminal in the folder containing `kobo_to_html.py`.

On Windows:

```bat
py kobo_to_html.py
```

Alternatively, double-click `run_windows.bat` if it is included.

On macOS or Linux:

```bash
python3 kobo_to_html.py
```

Some Linux distributions require Tkinter to be installed separately. For example, on Ubuntu or Debian:

```bash
sudo apt install python3-tk
```

## Export your annotations

1. Connect your Kobo to your computer using USB.
2. Accept the connection prompt on the Kobo.
3. Start Kobo Annotations Exporter.
4. Click `Choose .kobo folder…`.
5. Select the `.kobo` folder or the Kobo drive root.
6. Search for and select the books you want.
7. Choose an export option:
   - `Export individual files…`: creates one HTML file per selected book.
   - `Export combined file…`: creates one HTML notebook containing all selected books.
8. Choose the output location.

For a single book, the application asks where to save its HTML file. For multiple individual exports, it asks for an output folder.

Existing individual export filenames receive a numbered suffix instead of being overwritten.

Ctrl/Cmd-click or Shift-click to select multiple books. `Select visible` selects the books currently shown by the filter.

If `.kobo` is hidden, selecting the Kobo drive root avoids needing to reveal hidden folders.

## Use the exported HTML

### Copy text

Click `Copy highlight` or `Copy note` beside the relevant entry.

If browser clipboard access fails, the application may offer a manual-copy prompt.

### Change the notebook theme

Click `Switch to dark mode` or `Switch to light mode` in the notebook toolbar.

The notebook opens in light mode by default. The theme selection applies to the current session and does not change the background of generated quote images.

### Create a quote image

1. Click `Create quote image` or `Create note image`.
2. Choose a background colour.
3. Optionally select:
   - `Include book name`
   - `Include author name`
4. Review the preview.
5. Click `Copy image` or `Download PNG`.

Both attribution checkboxes start unchecked each time the editor opens.

Images are generated locally in your browser. If the text cannot fit within the supported font-size range, the editor displays a message instead of cropping it.

Image pasting only works in applications and fields that accept images.

### Print or save as PDF

Click `Print / Save as PDF` and choose the appropriate destination in your browser's print dialog.

## Clipboard compatibility

Clipboard functionality depends on browser support, permissions, and security settings.

If image copying is unavailable or blocked:

- Use `Download PNG`.
- Try a current browser with image clipboard support.
- Try opening the HTML through a local web server rather than directly from disk.

To serve an export folder locally, open a terminal in that folder and run:

```bat
py -m http.server 8000 --bind 127.0.0.1
```

Then visit:

```text
http://localhost:8000
```

Choose your exported HTML file. Press Ctrl+C in the terminal to stop the server.

Python is needed only for this optional local-server method, not for ordinary use of the packaged Windows application.

## Build a Windows executable

Build on Windows using a Python installation compatible with your intended users' systems.

Install PyInstaller:

```bat
py -m pip install --upgrade pyinstaller
```

Place `app_icon.ico` beside `kobo_to_html.py`, then run:

```bat
py -m PyInstaller --clean --onefile --windowed --name "Kobo_Annotations_Exporter" --icon "app_icon.ico" --add-data "app_icon.ico:." kobo_to_html.py
```

The executable is created in:

```text
dist/Kobo_Annotations_Exporter.exe
```

Share the executable, not the `build` folder. The icon is included in the packaged application.

Rebuild whenever you change the source code; existing executables do not update automatically.

Windows builds are not directly usable on macOS or Linux. Separate builds and testing are required for other platforms.

## Development workflow

Create a feature branch from an up-to-date `main`:

```bash
git switch main
git pull --ff-only origin main
git switch -c feature/your-feature-name
```

Make changes, test them, then commit the relevant files and push the branch:

```bash
git add path/to/changed-file
git commit -m "Describe the change"
git push -u origin feature/your-feature-name
```

Merge only after successful testing, using a pull request or a local merge.

If tests are included, run them from the folder containing the application and test file:

```bat
py -m unittest test_kobo_to_html.py
```

These tests do not replace manual testing of browser features or the packaged executable.

## Limitations

- Exports text highlights and typed notes, not handwritten drawings or notebook files.
- Reads only annotations present in the selected Kobo database.
- Does not fetch cloud-only annotations.
- Orders entries by creation date rather than their position in the book.
- Source locations are not Kindle locations or reliable printed page numbers.
- Available metadata varies by book format and database contents.
- Firmware or database-schema changes may require application updates.
- Browser clipboard support varies.
- Very long quotes may not fit in a single square image.
- New features appear only in newly generated HTML exports.
- Compatibility has not been verified on every Kobo model, firmware version, or Windows configuration.

## Privacy and backups

The application reads the Kobo database without intentionally changing it and does not upload your annotations.

Keep the Kobo connected while the application loads the database. Maintain a backup of important reading data.

Exported HTML files and images may contain personal notes and copyrighted excerpts. Review them before sharing.

Do not commit your Kobo database or personal exports to a public repository.

Recommended `.gitignore` entries:

```gitignore
__pycache__/
*.py[cod]
.venv/
venv/
build/
dist/
.kobo/
.Kobo/
*.sqlite
*.sqlite-*
*.db
*.db-*
exports/
```

## Feedback and contributions

Report bugs and suggest improvements through the repository's Issues tab.

For bug reports, include:

- Operating system.
- Source-run or executable version.
- Steps to reproduce the problem.
- Exact error message, if available.
- Browser name for HTML or clipboard issues.

Do not attach a personal Kobo database or private annotations publicly.