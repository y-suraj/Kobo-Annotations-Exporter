#!/usr/bin/env python3
"""Local, read-only Kobo annotation exporter. Python 3.9+."""
import html
import re
import sqlite3
import webbrowser
from pathlib import Path
from datetime import datetime


def esc(value):
    return html.escape(str(value or ''), quote=True)


def columns(db, table):
    return {r[1].lower(): r[1] for r in db.execute('PRAGMA table_info("' + table + '")')}


def load_books(folder):
    folder = Path(folder).expanduser().resolve()
    candidates = [folder / 'KoboReader.sqlite', folder / '.kobo' / 'KoboReader.sqlite', folder / '.Kobo' / 'KoboReader.sqlite']
    path = next((p for p in candidates if p.is_file()), None)
    if path is None:
        raise ValueError('KoboReader.sqlite was not found. Select .kobo or the Kobo drive root.')
    # SQLite backup reads a consistent snapshot, including an existing WAL.
    source = sqlite3.connect(path.as_uri() + '?mode=ro', uri=True, timeout=5)
    db = sqlite3.connect(':memory:')
    db.row_factory = sqlite3.Row
    try:
        source.backup(db)
    finally:
        source.close()
    try:
        bc = columns(db, 'Bookmark')
        if not {'volumeid', 'text', 'annotation'}.issubset(bc):
            raise ValueError('Unsupported database: Bookmark requires VolumeID, Text and Annotation columns.')
        cc = columns(db, 'content')
        metadata = {}
        if 'contentid' in cc:
            for row in db.execute('SELECT * FROM content'):
                item = {k.lower(): row[k] for k in row.keys()}
                metadata[str(item['contentid'])] = item
        books = {}
        for row in db.execute('SELECT * FROM Bookmark'):
            item = {k.lower(): row[k] for k in row.keys()}
            hidden = item.get('hidden')
            if str(hidden).strip().lower() in ('1', 'true'):
                continue
            text, note = item.get('text') or '', item.get('annotation') or ''
            if not str(text).strip() and not str(note).strip():
                continue
            volume = str(item['volumeid'] or '')
            chapter = metadata.get(str(item.get('contentid') or ''), {})
            main = metadata.get(volume, {})
            fallback = volume.replace('\\', '/').rsplit('/', 1)[-1] or 'Unknown book'
            title = main.get('title') or chapter.get('booktitle') or fallback
            author = main.get('attribution') or chapter.get('attribution') or 'Unknown author'
            book = books.setdefault(volume, {'id': volume, 'title': str(title), 'author': str(author), 'items': []})
            item['chapter'] = chapter.get('title') if str(item.get('contentid')) != volume else ''
            book['items'].append(item)
        # Dates are portable across EPUB/KEPUB; location paths are not page numbers.
        for book in books.values():
            book['items'].sort(key=lambda a: (str(a.get('datecreated') or ''), str(a.get('bookmarkid') or '')))
        return sorted(books.values(), key=lambda b: (b['title'].casefold(), b['author'].casefold(), b['id']))
    finally:
        db.close()


CSS = '\n:root { color-scheme: light; --ink:#25282e; --muted:#69717d; --line:#e0e3e8; }\n* { box-sizing:border-box; } body { margin:0; color:var(--ink); background:#f4f5f7; font:16px/1.65 system-ui,-apple-system,Segoe UI,sans-serif; }\nmain { max-width:940px; margin:38px auto; padding:38px 48px; background:white; border:1px solid var(--line); border-radius:12px; }\nh1 { font-size:30px; line-height:1.2; margin:0 0 8px; } h2 { font-size:25px; line-height:1.3; margin:0; }\n.subtitle,.meta,.author { color:var(--muted); } .subtitle { margin-top:0; } .author { margin:6px 0 22px; }\nnav { padding:20px; background:#f6f7f9; border-radius:8px; } a { color:#345d9d; } nav a { display:block; }\n.book { margin-top:44px; scroll-margin-top:20px; } .entry { padding:22px 0; border-top:1px solid var(--line); }\n.meta { font-size:13px; margin-bottom:10px; } blockquote { margin:0; padding:3px 0 3px 18px; border-left:3px solid #e3b849; white-space:pre-wrap; font:18px/1.75 Georgia,serif; overflow-wrap:anywhere; }\n.note { margin-top:14px; padding:14px 18px; background:#f7f8fa; border-radius:6px; white-space:pre-wrap; overflow-wrap:anywhere; }\n.note-label { font-size:12px; text-transform:uppercase; letter-spacing:.07em; color:var(--muted); display:block; }\n.toolbar { display:flex; gap:10px; margin:22px 0; } button { padding:8px 15px; border:1px solid #ccd1d8; border-radius:5px; background:white; cursor:pointer; }\nfooter { margin-top:36px; color:var(--muted); font-size:12px; } .location { overflow-wrap:anywhere; }\n@media(max-width:650px) { main { margin:0; border:0; border-radius:0; padding:25px 20px; } }\n@media print { body { background:white; } main { max-width:none; margin:0; padding:0; border:0; } .toolbar { display:none; } .entry { break-inside:avoid; } a { color:inherit; } }\n'


def render_html(books):
    count = sum(len(b['items']) for b in books)
    parts = ['<!doctype html><html lang="en"><head><meta charset="utf-8">',
             '<meta name="viewport" content="width=device-width,initial-scale=1">',
             '<title>Kobo — Notes and Highlights</title><style>' + CSS + '</style></head><body><main>',
             '<h1>Notes and Highlights</h1>',
             f'<p class="subtitle">Kobo notebook · {len(books)} book(s) · {count} annotation(s)</p>',
             '<div class="toolbar"><button onclick="window.print()">Print / Save as PDF</button></div><nav aria-label="Books">']
    for i, book in enumerate(books):
        parts.append(f'<a href="#book-{i}">{esc(book["title"])} — {len(book["items"])} annotation(s)</a>')
    parts.append('</nav>')
    for i, book in enumerate(books):
        parts.extend([f'<section class="book" id="book-{i}"><h2>{esc(book["title"])}</h2>', f'<p class="author">{esc(book["author"])}</p>'])
        for n, item in enumerate(book['items'], 1):
            kind = 'Highlight + Note' if item.get('text') and item.get('annotation') else ('Highlight' if item.get('text') else 'Note')
            labels = [kind + ' ' + str(n)]
            if item.get('chapter'):
                labels.append(str(item['chapter']))
            if item.get('datecreated'):
                labels.append(str(item['datecreated']))
            parts.append('<article class="entry"><div class="meta">' + esc(' · '.join(labels)) + '</div>')
            if item.get('text'):
                parts.append('<blockquote>' + esc(item['text']) + '</blockquote>')
            if item.get('annotation'):
                parts.append('<div class="note"><span class="note-label">Your note</span>' + esc(item['annotation']) + '</div>')
            location = item.get('startcontainerpath')
            if location:
                parts.append('<details class="meta location"><summary>Source location</summary>' + esc(location) + '</details>')
            parts.append('</article>')
        parts.append('</section>')
    parts.append('<footer>Exported locally on ' + esc(datetime.now().strftime('%Y-%m-%d %H:%M')) + '. Entries are ordered by creation date. Source locations are not Kindle locations or reliable page numbers.</footer></main></body></html>')
    return '\n'.join(parts)


class App:
    def __init__(self, root):
        self.root = root
        self.books = []
        root.title('Kobo to HTML — Notes and Highlights')
        root.geometry('960x640')
        root.minsize(650, 440)
        frame = ttk.Frame(root, padding=18)
        frame.pack(fill='both', expand=True)
        ttk.Label(frame, text='Kobo Notes & Highlights', font=('', 19, 'bold')).pack(anchor='w')
        ttk.Label(frame, text='Choose .kobo, select books, then export a browser-ready notebook.').pack(anchor='w', pady=(3, 15))
        bar = ttk.Frame(frame); bar.pack(fill='x')
        ttk.Button(bar, text='Choose .kobo folder…', command=self.choose).pack(side='left')
        self.path_label = ttk.Label(bar, text='No folder selected'); self.path_label.pack(side='left', padx=12)
        search = ttk.Frame(frame); search.pack(fill='x', pady=12)
        ttk.Label(search, text='Filter books:').pack(side='left')
        self.query = tk.StringVar()
        ttk.Entry(search, textvariable=self.query).pack(side='left', fill='x', expand=True, padx=8)
        self.query.trace_add('write', lambda *_: self.refresh())
        ttk.Button(search, text='Select visible', command=lambda: self.tree.selection_set(self.tree.get_children())).pack(side='left')
        ttk.Button(search, text='Clear selection', command=lambda: self.tree.selection_remove(self.tree.selection())).pack(side='left', padx=(6,0))
        table = ttk.Frame(frame); table.pack(fill='both', expand=True)
        self.tree = ttk.Treeview(table, columns=('title','author','count'), show='headings', selectmode='extended')
        for name, title, width in [('title','Book',460),('author','Author',260),('count','Annotations',100)]:
            self.tree.heading(name, text=title); self.tree.column(name, width=width, minwidth=70)
        self.tree.pack(side='left', fill='both', expand=True)
        scroll = ttk.Scrollbar(table, orient='vertical', command=self.tree.yview); scroll.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.bind('<<TreeviewSelect>>', lambda _: self.status_update())
        bottom=ttk.Frame(frame); bottom.pack(fill='x', pady=(14,0))
        self.open_after = tk.BooleanVar(value=True)
        ttk.Checkbutton(bottom, text='Open HTML after export', variable=self.open_after).pack(side='left')
        ttk.Button(bottom, text='Export selected books…', command=self.export).pack(side='right')
        self.status = ttk.Label(frame, text='Connect your Kobo by USB and allow the computer connection.'); self.status.pack(anchor='w', pady=(12,0))

    def choose(self):
        folder = filedialog.askdirectory(title='Select .kobo folder or Kobo drive root', mustexist=True)
        if not folder: return
        try:
            self.books = load_books(folder)
        except Exception as exc:
            messagebox.showerror('Could not load Kobo', str(exc)); return
        self.path_label.config(text=folder)
        self.refresh()
        if not self.books:
            messagebox.showinfo('No annotations', 'No visible text highlights or notes were found in this database.')

    def refresh(self):
        selected = set(self.tree.selection())
        self.tree.delete(*self.tree.get_children())
        query=self.query.get().casefold().strip()
        for i, book in enumerate(self.books):
            if query in (book['title'] + ' ' + book['author']).casefold():
                self.tree.insert('', 'end', iid=str(i), values=(book['title'],book['author'],len(book['items'])))
                if str(i) in selected: self.tree.selection_add(str(i))
        self.status_update()

    def status_update(self):
        self.status.config(text=f'{len(self.books)} annotated book(s) loaded · {len(self.tree.get_children())} visible · {len(self.tree.selection())} selected. Ctrl/Cmd-click or Shift-click to select multiple.')

    def export(self):
        selected = [self.books[int(i)] for i in self.tree.selection()]
        if not selected:
            messagebox.showinfo('Select books', 'Select one or more books first.'); return
        name = selected[0]['title'] if len(selected)==1 else 'Kobo Notes and Highlights'
        name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', name).strip(' .')[:100] or 'Kobo Notebook'
        target = filedialog.asksaveasfilename(title='Save HTML notebook', initialfile=name+'.html', defaultextension='.html', filetypes=[('HTML file','*.html')])
        if not target: return
        try:
            Path(target).write_text(render_html(selected), encoding='utf-8')
            self.status.config(text=f'Exported {len(selected)} book(s) to {target}')
            if self.open_after.get(): webbrowser.open(Path(target).resolve().as_uri())
        except Exception as exc:
            messagebox.showerror('Export failed', str(exc))


if __name__ == '__main__':
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox
    root = tk.Tk()
    App(root)
    root.mainloop()
