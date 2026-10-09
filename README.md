# Kobo to HTML

A local desktop application that exports selected books’ text highlights and typed notes from KoboReader.sqlite to a self-contained, Kindle-inspired HTML notebook.

## Run
Requires Python 3.9 or newer with Tkinter. No pip packages, accounts, internet connection, or cloud upload required.

Windows: install Python with Tkinter (standard installer), then double-click run_windows.bat, or run `py kobo_to_html.py`.
macOS: use a Python installation with Tkinter, then run `python3 kobo_to_html.py` in Terminal from the extracted folder.
Ubuntu/Debian: install `python3-tk` if necessary, then run `python3 kobo_to_html.py`.

## Use
1. Connect Kobo to your computer over USB and accept its connection prompt.
2. Start the app and click Choose .kobo folder.
3. Select .kobo, or just select the Kobo drive root if the hidden folder is not visible.
4. Search by title or author. Use Ctrl/Cmd-click or Shift-click to select multiple books, or Select visible.
5. Click Export selected books and choose an HTML destination.
6. Open the HTML in any modern browser. Use its Print / Save as PDF button if desired.

All selected books are included in one HTML file with a clickable table of contents. To make individual files, select and export one book at a time. Filtering removes hidden selections; selection applies only to currently displayed books.

## Safety and privacy
The source is opened with SQLite mode=ro. SQLite’s backup API creates an in-memory consistent snapshot rather than modifying the Kobo database. Keep the Kobo connected while loading; after books have loaded, the app uses that snapshot’s extracted data and no longer needs the device. Do not edit the live database or unplug during loading. Reading a WAL database may require an accessible existing SQLite shared-memory file; if permission errors occur, work from a complete offline database backup including any existing -wal and -shm companions. The app never uploads data. Treat exports as private: they include your highlights and personal notes.

## Scope and limitations
- Reads Bookmark.Text and Bookmark.Annotation, resolves book metadata by VolumeID and chapter metadata by ContentID.
- Excludes Hidden entries and bookmarks with no text or typed note.
- Supports note-only entries, Unicode text, and HTML escaping of all database-derived content.
- Falls back to chapter book title or volume identifier when book metadata is missing.
- Sorts annotations by creation date, not their position in the book; location formats differ between EPUB and KEPUB.
- Displays original source location when available, not invented page numbers or Kindle locations.
- Does not extract handwritten/stylus drawings, notebook files, or images from ExtraAnnotationData.
- Only exports annotations present in the selected database. Does not download cloud-only notes.
- Schema-aware optional fields are supported, but future firmware changes may need adaptation.
- Large databases may briefly pause the interface while loading. This version is a Python desktop app, not a precompiled executable.

## Testing
Run `python -m unittest test_kobo_to_html.py` (or `python3`). Synthetic tests cover selection data extraction, hidden/bookmark filtering, notes without highlights, metadata fallback, root folder selection, and escaping. A sample HTML export is included and contains fictional data only. Physical Kobo hardware and OS-specific GUI behavior have not been tested.
