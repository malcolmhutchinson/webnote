"""webnote.picture classes.
"""

import exifread
import os

from directory import Directory



from metadata import Metadata
import settings
from webnote import Webnote






class Picture():
    """Analyse and process an image file.

    A picture is any image file, whether it can be displayed inline or
    not. This class will find and create viewable thumbnail copies at
    512 and 1024 pixels. It will supply the appropriate links and urls
    to have it displaying in a web page.

    """
    docroot = None
    address = None
    baseurl = None
    staticroot = None
    parent = None
    
    def __init__(self, filename, docroot=None, baseurl=None,
                 data=None, staticroot=None):
        """
        """

        if not os.path.isfile(filename):
            raise self.FileNotFound(docroot)

        self.filename = filename
        (self.parentpath, self.fname) = os.path.split(filename)
        self.docroot = docroot
        self.baseurl = baseurl

        self.parent = Directory(
            self.parentpath, docroot=docroot, baseurl=baseurl
        )

        if not staticroot:
            staticroot = settings.STATIC_URL

        self.staticroot = staticroot
        self.data = data    

    class FileNotFound(Exception):
        def __init__(self, value):
            self.value = value

        def __str__(self):
            return repr(self.value)

    def __unicode__(self):
        return self.fname
        
    def __get_absolute_url__(self):

        address = self.filename.replace(self.docroot + '/', '')
        (path, fname) = os.path.split(address)
        (basename, ext) = os.path.splitext(fname)
        
        url = os.path.join(self.baseurl, path, 'picture', basename)

        return url
    
    url = property(__get_absolute_url__)


    def _get_img_src_(self):
        url = os.path.join(
            self.staticroot,
            self.filename.replace(
                self.docroot, self.staticroot + self.baseurl)
        )
        return url

    src = property(_get_img_src_)
    
    def alt(self):
        """Return the text in an tag alt attribute."""

        return self.fname

    def fname512(self):
        """Return a string filename to the 512px copy."""

        (basename, ext) = os.path.splitext(self.fname)
        return os.path.join(self.d512(), basename + '_512px' + ext.lower())
        
    def d1024(self):
        """Return the pathname to the 1024px directory."""

    def d512(self):
        """Return the pathname to the 512px directory."""

        d = os.path.join(
            self.parentpath,
            settings.FILEMAP_PICTURES['512px'][0])

        return d

    def gpxfiles(self):
        print "HERE"
        return self.parent.model['gpx']


        
    def make_thumbnails(self):
        """Create thumbnail copies at 512 and 1024 pix."""

    def title(self):
        """A string containing a title."""

        return self.fname

    def url512(self):
        """Return a url to the 512 px copy. """

        if os.path.isfile(self.fname512):
            url = os.path.join(

            )
            return url


        return self.url
