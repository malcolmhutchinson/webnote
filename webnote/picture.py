"""webnote.picture classes.
"""

import exifread
import os


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
    
    def __init__(self, docroot, baseurl, filename=None,
                 data=None, staticroot=None):
        """
        """

        if not os.path.isdir(docroot):
            raise self.DocrootNotFound(docroot)



    class DocrootNotFound(Exception):
        def __init__(self, value):
            self.value = value

        def __str__(self):
            return repr(self.value)



    def dir_1024(self):
        """Return the pathname to the 1024px directory."""

    def dir_512(self):
        """Return the pathname to the 512px directory."""

    def make_thumbnails(self):
        """Create thumbnail copies at 512 and 1024 pix."""
