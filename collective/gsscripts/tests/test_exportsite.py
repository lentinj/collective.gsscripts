from .. import exportsite

import os, os.path
import shutil
import tempfile
import unittest

HERE = os.path.abspath(os.path.dirname(__file__))
BASELINE_TAR = os.path.join(HERE,'test_data.tar.gz')
BASELINE_CONTENT = [
                './structure',
                'structure/paddock','structure/meadow','structure/.objects.xml',
                'structure/paddock/percy','structure/paddock/george','structure/paddock/_content.json','structure/paddock/.objects.xml',
                'structure/paddock/percy/_content.json','structure/paddock/percy/_field_feeding_notes.htm',
                'structure/paddock/george/_content.json','structure/paddock/george/_field_feeding_notes.htm',
                'structure/meadow/daisy','structure/meadow/freda','structure/meadow/_content.json','structure/meadow/.objects.xml',
                'structure/meadow/daisy/_content.json','structure/meadow/daisy/_field_feeding_notes.htm',
                'structure/meadow/freda/_content.json','structure/meadow/freda/_field_feeding_notes.htm',
]

class ExportSiteTests(unittest.TestCase):

    def test_fill_empty(self):
        """Can we fill an empty directory structure?"""
        try:
            tdir = tempfile.mkdtemp('test_exportsite')
            exportsite.merge_tar(open(BASELINE_TAR,'r'), tdir)
            self.assertDirectoryStructure(tdir, BASELINE_CONTENT)
        finally:
            shutil.rmtree(tdir)

    def test_replace_files(self):
        """Make sure files can be replaced & removed (apart from at the root)"""
        try:
            tdir = tempfile.mkdtemp('test_exportsite')
            exportsite.merge_tar(open(BASELINE_TAR,'r'), tdir)
            self.assertDirectoryStructure(tdir, BASELINE_CONTENT)

            # Modify a file, the size should change
            modified_file = os.path.join(tdir,'structure/meadow/daisy/_field_feeding_notes.htm')
            self.assertEqual(os.path.getsize(modified_file),44)
            with open(modified_file,'w') as f: f.write("I'm a little teapot")
            self.assertEqual(os.path.getsize(modified_file),19)

            # Add a previously-missing file
            new_file = os.path.join(tdir,'structure/meadow/daisy/_field_tasting_notes.htm')
            with open(new_file,'w') as f: f.write("I'm a little teapot")
            self.assertExists(new_file)

            # Add something at the root
            root_file = os.path.join(tdir,'should_be_ignored')
            with open(root_file,'w') as f: f.write("I'm a little teapot")
            self.assertExists(root_file)

            # Re-export, changes should have vanished apart from new root file
            exportsite.merge_tar(open(os.path.join(HERE,'test_data.tar.gz'),'r'), tdir)
            self.assertEqual(os.path.getsize(modified_file),44)
            self.assertMissing(new_file)
            self.assertExists(root_file)
        finally:
            shutil.rmtree(tdir)

    def test_replace_trees(self):
        """Make sure entire directories can be added & removed"""
        try:
            tdir = tempfile.mkdtemp('test_exportsite')
            exportsite.merge_tar(open(BASELINE_TAR,'r'), tdir)
            self.assertDirectoryStructure(tdir, BASELINE_CONTENT)

            # Create new pig called gelda
            shutil.copytree(os.path.join(tdir,'structure/paddock/percy'),os.path.join(tdir,'structure/paddock/gelda'))
            self.assertExists(tdir,'structure/paddock/gelda')
            self.assertExists(tdir,'structure/paddock/gelda/_field_feeding_notes.htm')

            # Remove daisy the cow
            shutil.rmtree(os.path.join(tdir,'structure/meadow/daisy'))
            self.assertMissing(tdir,'structure/meadow/daisy/_field_feeding_notes.htm')
            
            # Re-export, changes should have vanished apart from .svn directories
            exportsite.merge_tar(open(os.path.join(HERE,'test_data.tar.gz'),'r'), tdir)
            self.assertMissing(tdir,'structure/paddock/gelda')
            self.assertMissing(tdir,'structure/paddock/gelda/_field_feeding_notes.htm')
            self.assertExists(tdir,'structure/meadow/daisy/_field_feeding_notes.htm')
        finally:
            shutil.rmtree(tdir)

    def test_preserve_svn(self):
        """Make sure .svn directories are left untouched"""
        try:
            tdir = tempfile.mkdtemp('test_exportsite')
            exportsite.merge_tar(open(BASELINE_TAR,'r'), tdir)
            self.assertDirectoryStructure(tdir, BASELINE_CONTENT)

            # Create new pig called gelda
            shutil.copytree(os.path.join(tdir,'structure/paddock/percy'),os.path.join(tdir,'structure/paddock/gelda'))
            self.assertExists(tdir,'structure/paddock/gelda')
            self.assertExists(tdir,'structure/paddock/gelda/_field_feeding_notes.htm')

            # Scatter some fake .svn directories about
            self._fake_svn_dir(tdir,'structure/paddock/gelda')
            self._fake_svn_dir(tdir,'structure/paddock')
            self._fake_svn_dir(tdir,'structure')
            
            # Re-export, changes should have vanished, but .svn structure remains
            exportsite.merge_tar(open(os.path.join(HERE,'test_data.tar.gz'),'r'), tdir)
            self.assertExists(tdir,'structure/paddock/gelda') # Still here, it's got an .svn directory in it
            self.assertMissing(tdir,'structure/paddock/gelda/_field_feeding_notes.htm')
            self.assertSvnDir(tdir,'structure/paddock/gelda')
            self.assertSvnDir(tdir,'structure/paddock')
            self.assertSvnDir(tdir,'structure')
        finally:
            shutil.rmtree(tdir)

    def assertDirectoryStructure(self,actual,expected):
        rv = []
        for root, dirs, files in os.walk(actual):
            relpath = os.path.relpath(root,actual)
            for f in dirs + files:
                rv.append(os.path.join(relpath,f))
        self.assertEqual(rv,expected)

    def _fake_svn_dir(self,*kw):
        """Make something that looks like an .svn directory"""
        svn_dir = os.path.join(*kw + ('.svn',))
        tmp_dir = os.path.join(svn_dir,'tmp')
        os.mkdir(svn_dir)
        os.mkdir(tmp_dir)
        with open(os.path.join(svn_dir,'entries'),'w') as f: f.write('I am an entries file')
        for name in 'props','text-base','prop-base':
            os.mkdir(os.path.join(svn_dir,name))
            os.mkdir(os.path.join(tmp_dir,name))

    def assertSvnDir(self,*kw):
        """Checks an svn directory lives here"""
        self.assertExists(*kw+('.svn','entries'))
        self.assertExists(*kw+('.svn','tmp'))
        self.assertExists(*kw+('.svn','tmp','props'))
        self.assertExists(*kw+('.svn','props'))

    def assertExists(self,*kw):
        """Check combined path exists"""
        self.assertTrue(os.path.exists(os.path.join(*kw)))

    def assertMissing(self,*kw):
        """Check combined path doesn't exist"""
        self.assertFalse(os.path.exists(os.path.join(*kw)))
