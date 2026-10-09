import sqlite3
import tempfile
import unittest
from pathlib import Path
from kobo_to_html import load_books, render_html

class ExportTests(unittest.TestCase):
    def test_extract_and_escape(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)/'.kobo'; folder.mkdir()
            db=sqlite3.connect(folder/'KoboReader.sqlite')
            db.executescript('CREATE TABLE content(ContentID TEXT, Title TEXT, Attribution TEXT, BookTitle TEXT); CREATE TABLE Bookmark(BookmarkID TEXT, VolumeID TEXT, ContentID TEXT, Text TEXT, Annotation TEXT, Hidden INTEGER, DateCreated TEXT, StartContainerPath TEXT);')
            db.executemany('INSERT INTO content VALUES(?,?,?,?)', [('v','Book <one>','Author & Co',None),('chapter','Chapter 1','Author & Co','Book <one>')])
            db.executemany('INSERT INTO Bookmark VALUES(?,?,?,?,?,?,?,?)', [('1','v','chapter','<script>alert(1)</script>','My note',0,'2026-01-01','span#kobo.1.1'),('2','v','chapter',None,'Note only',0,'2026-01-02',None),('3','v','chapter','hidden',None,1,None,None),('4','v','chapter',None,None,0,None,None),('5','missing','chapter','Fallback',None,0,None,None)])
            db.commit(); db.close()
            original=(folder/'KoboReader.sqlite').read_bytes()
            books=load_books(tmp)
            self.assertEqual(len(books),2)
            book=next(b for b in books if b['id']=='v')
            self.assertEqual(len(book['items']),2)
            self.assertEqual(book['items'][1]['annotation'],'Note only')
            self.assertEqual(next(b for b in books if b['id']=='missing')['title'],'Book <one>')
            document=render_html([book])
            self.assertIn('&lt;script&gt;',document)
            self.assertNotIn('<script>',document)
            self.assertIn('Author &amp; Co',document)
            self.assertNotIn('hidden',document)
            self.assertEqual(original,(folder/'KoboReader.sqlite').read_bytes())
    def test_missing_database(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError): load_books(tmp)

if __name__=='__main__': unittest.main()
